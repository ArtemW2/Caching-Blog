from uuid import UUID

from src.application.dto import CreatePostDTO, PostDTO, UpdatePostDTO
from src.application.exceptions import CacheError, PostNotFoundError
from src.application.interfaces import CacheStorage
from src.application.mapper import PostMapper
from src.domain.entities import Post
from src.domain.factories import PostFactory
from src.domain.interfaces import PostRepository
from src.logger import get_logger

logger = get_logger(__name__)


class CreatePostUseCase:
    def __init__(
        self, mapper: PostMapper, repo: PostRepository, factory: PostFactory
    ) -> None:
        self.mapper: PostMapper = mapper
        self.repo: PostRepository = repo
        self.factory: PostFactory = factory

    async def __call__(self, create_dto: CreatePostDTO) -> PostDTO:
        post: Post = self.factory.create(create_dto.title, create_dto.text)
        await self.repo.save(post)

        logger.info(f"Публикация успешно сохранена в БД(ID={post.id})")
        return self.mapper.to_dto(post)


class GetPostUseCase:
    def __init__(
        self, mapper: PostMapper, repo: PostRepository, cache: CacheStorage
    ) -> None:
        self.mapper: PostMapper = mapper
        self.repo: PostRepository = repo
        self.cache: CacheStorage = cache

    async def __call__(self, post_id: UUID) -> PostDTO:
        try:
            cached_post = await self.cache.get(post_id)

            if cached_post is not None:
                logger.info(f"Публикация(ID={post_id}) найдена в кэше")
                return self.mapper.dict_to_dto(cached_post)
        except CacheError as e:
            logger.warning(
                f"Ошибка кэша ({type(e).__name__}): {e}. Перехожу к поиску данных в БД"
            )
            cached_post = None

        post: Post | None = await self.repo.get_by_id(post_id)

        if not post:
            logger.error(f"Публикация(ID={post_id}) не найдена")
            raise PostNotFoundError()

        post_dict: dict = self.mapper.to_dict(post)

        try:
            await self.cache.set(post.id, post_dict)
            logger.info(f"Публикация(ID={post.id}) сохранена в кэше")
        except CacheError as e:
            logger.warning(f"Ошибка при сохранении данных в кэше {type(e).__name__}: {e}")

        return self.mapper.to_dto(post)


class UpdatePostUseCase:
    def __init__(
        self, mapper: PostMapper, repo: PostRepository, cache: CacheStorage
    ) -> None:
        self.mapper: PostMapper = mapper
        self.repo: PostRepository = repo
        self.cache: CacheStorage = cache

    async def __call__(self, post_id: UUID, post_data: UpdatePostDTO) -> PostDTO:
        post: Post | None = await self.repo.get_by_id(post_id)

        if not post:
            logger.error(f"Публикация(ID={post_id}) не найдена")
            raise PostNotFoundError()

        post.update(post_data.title, post_data.text)
        await self.repo.update(post)
        logger.info(f"Публикация(ID={post_id}) успешно обновлена")
        
        try:
            await self.cache.invalidate(post_id)
            logger.info(f"Публикация(ID={post.id}) удалена из кэша")
        except CacheError as e:
            logger.warning(f"Ошибка при удалении данных из кэша {type(e).__name__}: {e}")

        return self.mapper.to_dto(post)


class DeletePostUseCase:
    def __init__(self, repo: PostRepository, cache: CacheStorage) -> None:
        self.repo: PostRepository = repo
        self.cache: CacheStorage = cache

    async def __call__(self, post_id: UUID) -> None:
        deleted: bool = await self.repo.delete(post_id)

        if not deleted:
            logger.error(f"Публикация(ID={post_id}) не найдена")
            raise PostNotFoundError()

        logger.info(f"Публикация(UD={post_id}) удалена из БД")
        try:
            await self.cache.invalidate(post_id)
            logger.info(f"Публикация(ID={post_id}) удалена из кэша")
        except CacheError as e:
            logger.warning(f"Ошибка при удалении данных из кэша {type(e).__name__}: {e}")
