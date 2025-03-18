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