import pytest
from http import HTTPStatus

from news.forms import BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db


COMMENT_TEXT = 'Тестовый комментарий'
BAD_COMMENT_TEXT = f'Плохое слово: {BAD_WORDS[0]}'
NEW_COMMENT_TEXT = 'Обновлённый текст'
FORM_DATA = {'text': COMMENT_TEXT}
BAD_FORM_DATA = {'text': BAD_COMMENT_TEXT}
EDIT_FORM_DATA = {'text': NEW_COMMENT_TEXT}


def test_anonymous_cannot_send_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    initial_count = Comment.objects.count()
    response = client.post(detail_url, FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count


def test_authorized_can_send_comment(client_author, author, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    initial_count = Comment.objects.count()
    response = client_author.post(detail_url, FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count + 1
    comment = Comment.objects.last()
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_words_not_created(client_author, detail_url):
    """Комментарий с запрещенными словами не создается."""
    initial_count = Comment.objects.count()
    response = client_author.post(detail_url, BAD_FORM_DATA)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert response.context['form'].has_error('text')
    assert Comment.objects.count() == initial_count


def test_author_can_edit_own_comment(client_author, comment, edit_url):
    """Автор может редактировать свой комментарий."""
    original_comment = Comment.objects.get(pk=comment.pk)
    response = client_author.post(edit_url, EDIT_FORM_DATA)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == original_comment.author
    assert comment.news == original_comment.news


def test_author_can_delete_own_comment(client_author, comment, delete_url):
    """Автор может удалить свой комментарий."""
    initial_count = Comment.objects.count()
    response = client_author.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_cannot_edit_comment(client_reader, comment, edit_url):
    """Читатель не может редактировать чужой комментарий."""
    original_comment = Comment.objects.get(pk=comment.pk)
    response = client_reader.post(edit_url, EDIT_FORM_DATA)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == original_comment.text
    assert comment.author == original_comment.author
    assert comment.news == original_comment.news


def test_reader_cannot_delete_comment(client_reader, comment, delete_url):
    """Читатель не может удалить чужой комментарий."""
    original_comment = Comment.objects.get(pk=comment.pk)
    initial_count = Comment.objects.count()
    response = client_reader.post(delete_url)
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    assert Comment.objects.filter(pk=comment.pk).exists()
    # Дополнительные проверки полей комментария
    assert comment.text == original_comment.text
    assert comment.author == original_comment.author
    assert comment.news == original_comment.news
    assert comment.created == original_comment.created
