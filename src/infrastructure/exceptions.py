from src.application.exceptions import CacheError, DatabaseError


# Redis
class RedisConnectionError(CacheError):
    def __init__(self, e: Exception) -> None:
        super().__init__(f'Ошибка при подключении к Redis: {e}')


class RedisResponseError(CacheError):
    def __init__(self, e: Exception) -> None:
        super().__init__(f"Ошибка при получении ответа от Redis: {e}")


class RedisTimeoutError(CacheError):
    def __init__(self, e: Exception) -> None:
        super().__init__(f"Истекло время ожидания ответа от Redis: {e}")


# SQLAlchemy

class DatabaseConnectionError(DatabaseError):
    def __init__(self, operation: str = "", e: Exception = None) -> None:
        super().__init__(f"Ошибка к БД при операции {operation}", e)


class DatabaseIntegrityError(DatabaseError):
    def __init__(self, e: Exception) -> None:
        super().__init__("Ошибка целостности данных при сохранении в БД", e)
