import torch
import torch.nn as nn


from ml_services.adain_model.modules import Encoder, MeanStdCalculator, AdaIN, Decoder


class AdainStyleTransferModel(nn.Module):
    def __init__(self, base_cnn: nn.Sequential):
        super(AdainStyleTransferModel, self).__init__()
        self.encoder = Encoder(base_cnn=base_cnn)
        self.adain = AdaIN()
        self.decoder = Decoder()
        self.mean_std_calc = MeanStdCalculator()

    def stylize(self, content: torch.Tensor, style: torch.Tensor, alpha: float = 1.0):
        """
        Функция стилизации, которая будет применяться при инференсе.
        * alpha - число [0, 1], степень переноса стиля
        """
        content_features = self.encoder(content,
                                        return_all_outputs=False)  # карты признаков контента с последнего слоя энкодера
        style_features = self.encoder(style,
                                      return_all_outputs=False)  # карты признаков стиля с последнего слоя энкодера

        adain_features = self.adain(content_features,
                                    style_features)  # модифицированные карты признаков контента (стилизованные)
        adain_features = alpha * adain_features + (
                    1 - alpha) * content_features  # контроль степени стилизации при помощи alpha

        outp = self.decoder(adain_features)  # получение стилизованного изображения исходного (512х512) размера

        return outp

    def __content_loss(self, result_enc_outp, adain_features):
        """
        * result_enc_outp - выход энкодера для D(adain_content), где D - декодер
        * adain_content - выход блока AdaIN, преобразованные фичи изначального контент-изображения
        """
        return torch.nn.MSELoss(reduction='mean')(result_enc_outp, adain_features)

    def __style_loss(self, result_enc_outputs, style_enc_outputs):
        """
        * result_enc_outputs - выходы всех рассмотренных выше слоев энкодера для полученной декодером стилизации
        * style_enc_outputs - выходы всех рассмотренных выше слоев энкодера для изображения стиля
        """
        style_loss_ = 0.0
        for result_outp, style_outp in zip(result_enc_outputs, style_enc_outputs):
            result_outp_mean, result_outp_std = self.mean_std_calc(result_outp)
            style_outp_mean, style_outp_std = self.mean_std_calc(style_outp)

            style_loss_ += torch.nn.MSELoss(reduction='mean')(result_outp_mean, style_outp_mean) + torch.nn.MSELoss(
                reduction='mean')(result_outp_std, style_outp_std)

        return style_loss_

    def forward(self, content_images, style_images, alpha=1.0, style_weight=10):
        content_features = self.encoder(content_images)
        style_features = self.encoder(style_images)

        adain_features = self.adain(content_features, style_features)
        adain_features = alpha * adain_features + (1 - alpha) * content_features

        result = self.decoder(adain_features)

        result_features = self.encoder(result, return_all_outputs=False)
        result_all_features = self.encoder(result, return_all_outputs=True)
        style_all_features = self.encoder(style_images, return_all_outputs=True)

        content_loss = self.__content_loss(result_features, adain_features)
        style_loss = self.__style_loss(result_all_features, style_all_features)

        loss = content_loss + style_weight * style_loss

        return loss