class ApplicationError(Exception):
    pass

class PostNotFoundError(ApplicationError):
    def __init__(self):
        super().__init__("Интересующая Вас публикация не найдена")


class CacheError(ApplicationError):
    pass


class DatabaseError(ApplicationError):
    def __init__(self, message: str | None = None, e: Exception = None) -> None:
        if message is None:
            message = "Непредвиденная ошибка при взаимодействии с БД"
        super().__init__(f"{message}: {e}")