import torch
import torch.nn as nn
import torch.nn.functional as F


class ContentLoss(nn.Module):
    def __init__(self, target):
        super(ContentLoss, self).__init__()
        self.target = target.detach()

    def forward(self, inp):
        self.loss = F.mse_loss(inp, self.target)
        return inp


class StyleLoss(nn.Module):
    def __init__(self, target):
        super(StyleLoss, self).__init__()
        self.target = StyleLoss.gram_matrix(target).detach()

    @staticmethod
    def gram_matrix(inp):
        batch_size, nmaps, w, h = inp.size()

        features = inp.view(batch_size * nmaps, w * h)  # Получаем для каждой карты признаков вектор размера wxh

        G = torch.mm(features, features.T)

        return G.div(batch_size * nmaps * w * h)

    def forward(self, inp):
        G = StyleLoss.gram_matrix(inp)
        self.loss = F.mse_loss(G, self.target)
        return inp


class Normalization(nn.Module):
    def __init__(self, mean, std):
        super(Normalization, self).__init__()
        self.mean = torch.tensor(mean).view(-1, 1, 1)
        self.std = torch.tensor(std).view(-1, 1, 1)

    def forward(self, img):
        return (img - self.mean) / self.std