import torch

from torchvision.transforms import ToTensor, ToPILImage
from torchvision.models import vgg19

from celery_config import app

from utils import bytes_to_image, image_to_bytes
from ml_services.gatys_model import GatysModel, gatys_model_config
from ml_services.adain_model import AdainStyleTransferModel, preprocess_tensor, denorm_images


BASE_CNN = None

ADAIN_MODEL = None


@app.task()
def transfer_style_by_gatys(content: bytes, style: bytes, degree: int) -> bytes:

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


@app.task()
def transfer_style_by_adain(content: bytes, style: bytes, degree: int) -> bytes:
    global ADAIN_MODEL

    if ADAIN_MODEL is None:
        base_cnn = vgg19().features[:21]
        base_cnn_weights = torch.load('./ml_services/models/adain_encoder_weights.pt', map_location=torch.device('cpu'))
        base_cnn.load_state_dict(base_cnn_weights)

        ADAIN_MODEL = AdainStyleTransferModel(base_cnn)
        adain_weights = torch.load('./ml_services/models/adain_style_model.pt', map_location=torch.device('cpu'))
        ADAIN_MODEL.load_state_dict(adain_weights['model_state_dict'])

    imsize = (512, 512)

    alpha = {
        1: 0.2,
        2: 0.4,
        3: 0.6,
        4: 0.8,
        5: 1.0
    }

    content = preprocess_tensor(ToTensor()(bytes_to_image(content).resize(imsize)))
    style = preprocess_tensor(ToTensor()(bytes_to_image(style).resize(imsize)))

    output = ADAIN_MODEL.stylize(content, style, alpha=alpha[degree])

    output = denorm_images(output)[0]
    output.clamp_(0, 1)

    return image_to_bytes(ToPILImage()(output))