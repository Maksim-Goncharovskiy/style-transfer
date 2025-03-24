# Стилизация изображений
### Содержание
1. [Описание](#title1)
2. [Структура проекта](#title2)
3. [Технологии](#title3)
4. [Инструкция по установке и запуску](#title4)

## <a id="title1">1.Описание.</a>

## <a id="title2">2.Структура проекта.</a>
```
root/
├── tg-bot/          # Телеграм-бот
└── materials/       # Модели и данные
    ├── online-nst/  # Online Neural Style Transfer  
    ├── adain/       # Adaptive Instance Normalization  
    └── cycle-gan/   # CycleGAN
```

## <a id="title3">3.Технологии.</a>
### Tg-bot
* aiogram
* Redis - хранилище для FSM; брокер сообщений;
* Celery - очередь задач для выполнения стилизации в отдельном потоке;
### Ml-stack
* torch, torchvision
* MLflow (логгирование некоторых экспериментов)


## <a id="title3">4. Инструкция по установке и запуску.</a>
