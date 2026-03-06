import pytest

from src.domain.entities import Post
from src.domain.exceptions import PostDataError, PostTitleError
from src.domain.factories import PostFactory


def test_create_post_with_valid_data():
    factory = PostFactory()
    post = factory.create(title="Title", text="Text")

    assert post.title == "Title"
    assert post.text == "Text"


def test_create_post_with_empty_title_strip():
    with pytest.raises(PostTitleError, match="помимо пробелов"):
        factory = PostFactory()
        post: Post = factory.create(title=" ", text="Text")


def test_create_post_with_too_long_title():
    long_title = "a" * 51
    with pytest.raises(PostTitleError, match="50 символов"):
        factory = PostFactory()
        factory.create(title=long_title, text="content")


def test_create_post_with_empty_text():
    with pytest.raises(PostDataError, match="не может быть пустым"):
        factory = PostFactory()
        post = factory.create(title="Title", text="")


def test_update_post():
    factory = PostFactory()
    post = factory.create(title="Old", text="Old content")
    post.update(title="New", text="New content")
    assert post.title == "New"
    assert post.text == "New content"
    assert post.updated_at is not None


def test_incorrect_update_post():
    factory = PostFactory()
    post = factory.create(title="Old", text="Old content")

    with pytest.raises(PostDataError, match="не может быть пустым"):
        post.update(title="New", text="")
    
    with pytest.raises(PostTitleError, match="помимо пробелов"):
        post.update(title=" ", text="Old content")