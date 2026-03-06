class DomainError(Exception):
    pass


class PostTitleError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PostDataError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)