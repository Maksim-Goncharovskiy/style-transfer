import torch
from torchvision.transforms import Normalize


DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

VGG19_NORMALIZATION_MEAN = torch.tensor([0.485, 0.456, 0.406])
VGG19_NORMALIZATION_STD = torch.tensor([0.229, 0.224, 0.225])


def preprocess_tensor(tensor: torch.Tensor):
    return Normalize(VGG19_NORMALIZATION_MEAN, VGG19_NORMALIZATION_STD)(tensor[:3]).unsqueeze(0)


def denorm_images(images):
    """
    Денормализация изображений на выходе.
    Args:
        * images (torch.Tensor) : батч нормализованных картинок
    """
    means = torch.tensor(VGG19_NORMALIZATION_MEAN).reshape(1, 3, 1, 1).to(DEVICE)
    stds = torch.tensor(VGG19_NORMALIZATION_STD).reshape(1, 3, 1, 1).to(DEVICE)

    return images * stds + means