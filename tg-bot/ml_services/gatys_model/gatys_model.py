import torch
import torch.nn as nn
import torch.optim as optim
from ml_services.gatys_model.modules import Normalization, ContentLoss, StyleLoss

VGG19_NORMALIZATION_MEAN = torch.tensor([0.485, 0.456, 0.406])
VGG19_NORMALIZATION_STD = torch.tensor([0.229, 0.224, 0.225])

CONTENT_LAYERS_DEFAULT = ['Conv_4']
STYLE_LAYERS_DEFAULT = ['Conv_1', 'Conv_2', 'Conv_3', 'Conv_4', 'Conv_5']


class GatysModel:
    """
    Класс-интерфейс переноса стиля.
    """

    def __init__(self, base_cnn, content_img, style_img, device,
                 normalization_mean=VGG19_NORMALIZATION_MEAN,
                 normalization_std=VGG19_NORMALIZATION_STD,
                 content_layers=CONTENT_LAYERS_DEFAULT,
                 style_layers=STYLE_LAYERS_DEFAULT):

        content_img = content_img.to(device)
        style_img = style_img.to(device)
        self.model = nn.Sequential().to(device)
        self.content_losses = []
        self.style_losses = []

        self.model.add_module("ImageNorm", Normalization(mean=normalization_mean, std=normalization_std).to(device))

        conv_counter: int = 0
        module_name: str = ""

        for layer in base_cnn.children():
            if isinstance(layer, nn.Conv2d):
                conv_counter += 1
                module_name = f"Conv_{conv_counter}"

            elif isinstance(layer, nn.ReLU):
                module_name = f"ReLU_{conv_counter}"
                layer = nn.ReLU(inplace=False)

            elif isinstance(layer, nn.MaxPool2d):
                module_name = f"MaxPool2d_{conv_counter}"

            else:
                raise ValueError

            self.model.add_module(module_name, layer.to(device))

            if module_name in content_layers:
                target = self.model(content_img).detach().to(device)
                content_loss_module = ContentLoss(target)
                self.content_losses.append(content_loss_module)
                self.model.add_module(f"ContentLoss_{conv_counter}", content_loss_module)

            if module_name in style_layers:
                target = self.model(style_img).detach().to(device)
                style_loss_module = StyleLoss(target)
                self.style_losses.append(style_loss_module)
                self.model.add_module(f"StyleLoss_{conv_counter}", style_loss_module)

        self.model.to(device)

    def __repr__(self):
        return f'{self.__class__.__name__}(model = {self.model})'

    def transfer_style(self, input_image, device, optimizer_class=None, lr=0.05,
                       num_steps=300, style_weight=100000, content_weight=1,
                       scheduler_step: int | None = None, gamma=1.0):
        """
        Функция, реализующая алгоритм Гатиса. Итеративная оптимизация изображения для получения стилизации.
        """
        input_image = input_image.to(device)

        input_image.requires_grad = True
        self.model.eval()

        optimizer = None
        if not optimizer_class:
            optimizer = optim.Adam([input_image], lr=lr)
        else:
            optimizer = optimizer_class([input_image], lr=lr)

        scheduler = optim.lr_scheduler.ExponentialLR(optimizer=optimizer, gamma=gamma)

        for i in range(1, num_steps + 1):

            def closure():
                optimizer.zero_grad()

                self.model(input_image)
                content_final_loss = 0.0
                style_final_loss = 0.0

                for content_loss in self.content_losses:
                    content_final_loss += content_loss.loss

                for style_loss in self.style_losses:
                    style_final_loss += style_loss.loss

                loss = content_weight * content_final_loss + style_weight * style_final_loss
                loss.backward()

                return loss

            optimizer.step(closure)

            if scheduler_step:
                if i % scheduler_step == 0:
                    scheduler.step()

            with torch.no_grad():
                input_image.clamp_(0, 1)


        with torch.no_grad():
            input_image.clamp_(0, 1)

        return input_image