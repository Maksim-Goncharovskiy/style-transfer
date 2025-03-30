import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(self, base_cnn: nn.Sequential):
        super(Encoder, self).__init__()
        self.encoder = base_cnn

    def forward(self, inp, return_all_outputs=False):
        outp1 = self.encoder[:2](inp)  # relu_1_1
        outp2 = self.encoder[2:7](outp1)  # relu_2_1
        outp3 = self.encoder[7:12](outp2)  # relu_3_1
        outp4 = self.encoder[12:21](outp3)  # relu_4_1

        # для подсчёта потери стиля
        if return_all_outputs:
            return outp1, outp2, outp3, outp4

        return outp4



class MeanStdCalculator(nn.Module):
    """
    Модуль подсчёта среднего значения и стандартного отклонения по каждому каналу.
    Пригодится в блоке AdaIN, а также при вычислении потери стиля.
    """

    def __init__(self):
        super(MeanStdCalculator, self).__init__()

    def forward(self, feature_maps: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size = feature_maps.size()[0]
        channels = feature_maps.size()[1]

        mean = feature_maps.reshape(batch_size, channels, -1).mean(dim=2).reshape(batch_size, channels, 1, 1)
        std = feature_maps.reshape(batch_size, channels, -1).std(dim=2).reshape(batch_size, channels, 1, 1)

        return mean, std



class AdaIN(nn.Module):
    """
    Модуль адаптивной инстанс нормализации.
    Преобразует карты признаков контента согласно распределения карт признаков для стиля.
    """

    def __init__(self):
        super(AdaIN, self).__init__()
        self.mean_std_calc = MeanStdCalculator()

    def forward(self, content_features, style_features) -> torch.Tensor:
        content_mean, content_std = self.mean_std_calc(content_features)
        content_std = content_std + 1e-8
        style_mean, style_std = self.mean_std_calc(style_features)
        style_std = style_std + 1e-8

        norm_content = (content_features - content_mean) / content_std
        adapt_content = norm_content * style_std + style_mean

        return adapt_content



class Decoder(nn.Module):
    """
    Декодер должен хорошо научиться восстанавливать изображения,
    для этого понадобится использовать бОльшее количество свёрток чем 3.
    """

    def __init__(self):
        super(Decoder, self).__init__()

        self.block1 = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest')
        )

        self.block2 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest')
        )

        self.block3 = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 3, kernel_size=3, stride=1, padding=1)
        )

    def forward(self, inp):
        return self.block3(self.block2(self.block1(inp)))