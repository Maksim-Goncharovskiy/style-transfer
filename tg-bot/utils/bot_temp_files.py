"""
Модуль для работы с файлами пользователей в процессе получения стилизации: сохранение / удаление
"""
import os
import shutil
from .exceptions import TgBotDirNotFound, UserDirNotFound, UserFileNotFound, UserDirCreationError, UserDirDeletionError
from PIL import Image


TG_BOT_DIR = ""


async def create_bot_dir(tg_bot_dir: str):
    """
    Создание директории для сохранения временных файлов в процессе работы бота.

    Если такая директория уже существует, то ничего не происходит, значение глобальной переменной TG_BOT_DIR
    устанавливается, исключение FileExistsError не возникает.

    Может возникнуть исключение OSError, если недостаточно прав для создания директории по заданному пути или если
    путь не валиден. Это исключение должно быть обработано в вызывающем куске кода.
    """
    global TG_BOT_DIR
    TG_BOT_DIR = tg_bot_dir
    if not os.path.exists(TG_BOT_DIR):
        os.mkdir(TG_BOT_DIR)
        os.mkdir(os.path.join(TG_BOT_DIR, 'temp'))



async def create_user_temp_file(user_id: int, img: bytes, filename: str):
    """
    Сохраняет изображение img во временную директорию пользователя user_id.

    Перед сохранением выполняется проверка корректности файловой системы бота.
    """
    if not os.path.exists(os.path.join(TG_BOT_DIR, 'temp')):
        raise TgBotDirNotFound(f"Файловая система бота была нарушена. Директория {TG_BOT_DIR}/temp/ не найдена "
                               f"в процессе записи данных для пользователя {user_id}.")

    user_path = os.path.join(TG_BOT_DIR, 'temp', str(user_id))

    try:
        os.mkdir(user_path)
    except FileExistsError:
        pass
    except OSError as error:
        raise UserDirCreationError(f"{error} (Ошибка при создании директории для пользователя {user_id})")
    finally:
        with open(f"{user_path}/{filename}", "wb") as f:
            f.write(img)



async def read_user_temp_file(user_id: int, filename: str):
    """
    Чтение файла из директории пользователя.

    Сначала выполняется проверка корректности файловой системы бота.
    """
    bot_temp_dir_path = os.path.join(TG_BOT_DIR, 'temp')
    user_temp_dir_path = os.path.join(bot_temp_dir_path, str(user_id))
    user_temp_file_path = os.path.join(user_temp_dir_path, filename)

    if not os.path.exists(bot_temp_dir_path):
        raise TgBotDirNotFound(f"Файловая система бота была нарушена. Директория {TG_BOT_DIR}/temp/ не найдена "
                                   f"в процессе чтения данных для пользователя {user_id}.")

    elif not os.path.exists(user_temp_dir_path):
        raise UserDirNotFound(f"Файловая система бота была нарушена. Директория пользователя {user_id} не найдена"
                              f"в процессе чтения данных.")

    elif not os.path.exists(user_temp_file_path):
        raise UserFileNotFound(f"Файл {filename} не найден в папке пользователя {user_id}")

    else:
        return Image.open(user_temp_file_path)



async def delete_user_temp_dir(user_id: int):
    """
    Удаление временной директории пользователя.

    Сначала проверяется, что директория существует, потом происходит удаление.

    Если директория не существует, то ничего не делается.

    Если при удалении возникла какая-то ошибка, то полученное исключение оборачивается в UserDirDeletionError
    и пробрасываем дальше в вызывающий кусок кода.
    """
    bot_temp_dir_path = os.path.join(TG_BOT_DIR, 'temp')
    user_temp_dir_path = os.path.join(bot_temp_dir_path, str(user_id))
    if os.path.exists(user_temp_dir_path):
        try:
            shutil.rmtree(user_temp_dir_path)
        except OSError as error:
            raise UserDirDeletionError(f"{error} (Ошибка при удалении директории пользователя {user_id})")



async def get_user_dir_full_path(user_id: int) -> str:
    return os.path.join(TG_BOT_DIR, 'temp', str(user_id))