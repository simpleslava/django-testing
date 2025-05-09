import pytest
from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_cannot_send_comment(client, news):
    """Проверяет, что анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, {'text': 'Привет'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_authorized_can_send_comment(client_author, author, news):
    """Проверяет создание комментария авторизованным пользователем."""
    url = reverse('news:detail', args=[news.pk])
    payload = {'text': 'Тестовый комментарий'}
    response = client_author.post(url, payload)
    comment = Comment.objects.first()
    assert response.status_code == HTTPStatus.FOUND
    assert comment is not None
    assert comment.text == payload['text']
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_words_not_created(client_author, news):
    """Проверяет, что комментарий с нецензурным словом не создаётся."""
    url = reverse('news:detail', args=[news.pk])
    bad_word = BAD_WORDS[0]
    payload = {'text': f'Плохое слово: {bad_word}'}
    response = client_author.post(url, payload)
    form = response.context.get('form')
    assert form is not None
    assert 'text' in form.errors
    assert Comment.objects.count() == 0


def test_author_can_edit_own_comment(client_author, comment):
    """Проверяет возможность редактирования своего комментария автором."""
    url = reverse('news:edit', args=[comment.pk])
    new_text = 'Обновлённый текст'
    response = client_author.post(url, {'text': new_text})
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == new_text


def test_author_can_delete_own_comment(client_author, comment):
    """Проверяет возможность удаления своего комментария автором."""
    url = reverse('news:delete', args=[comment.pk])
    response = client_author.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url_name,payload,expected_status',
    [
        ('news:edit', {'text': 'Новый текст'}, HTTPStatus.NOT_FOUND),
        ('news:delete', {}, HTTPStatus.NOT_FOUND),
    ],
)
def test_reader_cannot_modify_comment(
    client_reader, comment, url_name, payload, expected_status
):
    """
    Проверяет, что пользователь не может изменить
    или удалить чужой комментарий.
    """
    url = reverse(url_name, args=[comment.pk])
    response = client_reader.post(url, payload)
    assert response.status_code == expected_status
    assert Comment.objects.filter(pk=comment.pk).exists()
