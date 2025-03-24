import torch

from torchvision.transforms import ToTensor, ToPILImage
from torchvision.models import vgg19

from celery_config import app

from utils import bytes_to_image, image_to_bytes
from ml_services.gatys_model import GatysModel, gatys_model_config


BASE_CNN = None


@app.task()
def transfer_style(content: bytes, style: bytes, degree: int) -> bytes:

    global BASE_CNN

    # Загружаем модель при самом первом запросе
    if BASE_CNN is None:
        vgg19_encoder_weights = torch.load('./ml_services/models/vgg19_encoder_weights.pt')

        BASE_CNN = vgg19().features[0 : 35]
        BASE_CNN.load_state_dict(vgg19_encoder_weights)

        BASE_CNN = BASE_CNN.to(gatys_model_config["DEVICE"])

        for param in BASE_CNN.parameters():
            param.requires_grad = False

    content = ToTensor()(bytes_to_image(content).resize(gatys_model_config["IMSIZE"]))[:3].unsqueeze(0)
    style = ToTensor()(bytes_to_image(style).resize(gatys_model_config["IMSIZE"]))[:3].unsqueeze(0)
    input_ = content.clone()

    degree = str(degree)

    style_model = GatysModel(
        base_cnn=BASE_CNN,
        content_img=content,
        style_img=style,
        device=gatys_model_config["DEVICE"],
        content_layers=gatys_model_config[degree]["CONTENT_LAYERS"],
        style_layers=gatys_model_config[degree]["STYLE_LAYERS"]
    )

    output = style_model.transfer_style(
        input_image=input_,
        device=gatys_model_config["DEVICE"],
        optimizer_class=gatys_model_config["OPTIMIZER"],
        lr=gatys_model_config[degree]["LR"],
        num_steps=gatys_model_config[degree]["NUM_STEPS"],
        style_weight=gatys_model_config[degree]["STYLE_WEIGHT"],
        scheduler_step=gatys_model_config[degree]["SCHEDULER_STEP"],
        gamma=gatys_model_config[degree]["GAMMA"]
    )

    return image_to_bytes(ToPILImage()(output[0]))