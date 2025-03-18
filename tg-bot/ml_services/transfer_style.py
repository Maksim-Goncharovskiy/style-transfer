import torch
import torch.optim as optim

from torchvision.transforms import Resize, ToTensor, ToPILImage
from torchvision.models import vgg19

from celery_config import app

from utils import bytes_to_image, image_to_bytes
from .style_model import StyleModel

BASE_CNN = None

model_config = {
    "DEVICE": torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'),
    "IMSIZE": (512, 512) if torch.cuda.is_available() else (256, 256),
    "OPTIMIZER": optim.Adam,
    "LR": 0.05,
    "NUM_STEPS": 75,
    "STYLE_WEIGHT": 10**8,
    "SCHEDULER_STEP": None,
    "GAMMA": 1.0,
    "CONTENT_LAYERS": [f'Conv_{i}' for i in range(12, 17)],
    "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 5)]
}


@app.task()
def transfer_style(content: bytes, style: bytes, degree: int) -> bytes:
    global BASE_CNN
    global model_config
    if BASE_CNN is None:
        BASE_CNN = vgg19(pretrained=True).features[0 : 35].to(model_config["DEVICE"])
        for param in BASE_CNN.parameters():
            param.requires_grad = False

    content = ToTensor()(bytes_to_image(content).resize((256, 256)))[:3].unsqueeze(0)
    style = ToTensor()(bytes_to_image(style).resize((256, 256)))[:3].unsqueeze(0)
    input_ = content.clone()

    style_model = StyleModel(
        base_cnn=BASE_CNN,
        content_img=content,
        style_img=style,
        device=model_config["DEVICE"],
        content_layers=model_config["CONTENT_LAYERS"],
        style_layers=model_config["STYLE_LAYERS"]
    )

    output = style_model.transfer_style(
        input_image=input_,
        device=model_config["DEVICE"],
        optimizer_class=model_config["OPTIMIZER"],
        lr=model_config["LR"],
        num_steps=model_config["NUM_STEPS"],
        style_weight=model_config["STYLE_WEIGHT"],
        scheduler_step=model_config["SCHEDULER_STEP"],
        gamma=model_config["GAMMA"]
    )

    return image_to_bytes(ToPILImage()(output[0]))