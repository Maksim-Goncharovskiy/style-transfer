"""
Модуль с кастомными исключениями для обработки исключительных ситуаций,
связанных с обработкой и хранением файлов на сервере.
"""

class BaseServerError(OSError):
    pass


class TgBotDirNotFound(BaseServerError):
    pass


class UserDirNotFound(BaseServerError):
    pass


class UserFileNotFound(BaseServerError):
    pass


class UserDirCreationError(BaseServerError):
    pass


class UserDirDeletionError(BaseServerError):
    pass