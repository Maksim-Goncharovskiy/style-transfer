import torch
import torch.optim as optim


gatys_model_config = {
    "DEVICE": torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'),
    "IMSIZE": (512, 512) if torch.cuda.is_available() else (256, 256),
    "OPTIMIZER": optim.Adam,
    "1": {
        "LR": 0.05,
        "NUM_STEPS": 20,
        "STYLE_WEIGHT": 10**8,
        "SCHEDULER_STEP": None,
        "GAMMA": 1.0,
        "CONTENT_LAYERS": [f'Conv_{i}' for i in range(14, 17)],
        "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 7)]
    },
    "2": {
        "LR": 0.05,
        "NUM_STEPS": 40,
        "STYLE_WEIGHT": 10**8,
        "SCHEDULER_STEP": None,
        "GAMMA": 1.0,
        "CONTENT_LAYERS": [f'Conv_{i}' for i in range(14, 17)],
        "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 9)]
    },
    "3": {
        "LR": 0.05,
        "NUM_STEPS": 60,
        "STYLE_WEIGHT": 10**8,
        "SCHEDULER_STEP": None,
        "GAMMA": 1.0,
        "CONTENT_LAYERS": [f'Conv_{i}' for i in range(14, 17)],
        "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 11)]
    },
    "4": {
        "LR": 0.05,
        "NUM_STEPS": 80,
        "STYLE_WEIGHT": 10**8,
        "SCHEDULER_STEP": None,
        "GAMMA": 1.0,
        "CONTENT_LAYERS": [f'Conv_{i}' for i in range(14, 17)],
        "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 13)]
    },
    "5": {
        "LR": 0.08,
        "NUM_STEPS": 100,
        "STYLE_WEIGHT": 10**8,
        "SCHEDULER_STEP": 25,
        "GAMMA": 0.85,
        "CONTENT_LAYERS": [],
        "STYLE_LAYERS": [f'Conv_{i}' for i in range(1, 17)]
    }
}