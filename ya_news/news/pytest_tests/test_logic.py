import pytest
from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db


COMMENT_TEXT = 'Тестовый комментарий'
BAD_COMMENT_TEXT = f'Плохое слово: {BAD_WORDS[0]}'


def test_anonymous_cannot_send_comment(client, news):
    url = reverse('news:detail', args=[news.pk])
    initial_count = Comment.objects.count()
    response = client.post(url, {'text': COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count


def test_authorized_can_send_comment(client_author, author, news):
    url = reverse('news:detail', args=[news.pk])
    initial_count = Comment.objects.count()
    response = client_author.post(url, {'text': COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count + 1
    comment = Comment.objects.last()
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_comment_with_bad_words_not_created(client_author, news):
    url = reverse('news:detail', args=[news.pk])
    initial_count = Comment.objects.count()
    response = client_author.post(url, {'text': BAD_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert response.context['form'].has_error('text')
    assert Comment.objects.count() == initial_count


def test_author_can_edit_own_comment(client_author, comment):
    url = reverse('news:edit', args=[comment.pk])
    new_text = 'Обновлённый текст'
    response = client_author.post(url, {'text': new_text})
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == new_text
    assert comment.author == comment.author
    assert comment.news == comment.news


def test_author_can_delete_own_comment(client_author, comment):
    url = reverse('news:delete', args=[comment.pk])
    initial_count = Comment.objects.count()
    response = client_author.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count - 1


def test_reader_cannot_edit_comment(client_reader, comment):
    url = reverse('news:edit', args=[comment.pk])
    original_text = comment.text
    response = client_reader.post(url, {'text': 'Новый текст'})
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == original_text


def test_reader_cannot_delete_comment(client_reader, comment):
    url = reverse('news:delete', args=[comment.pk])
    initial_count = Comment.objects.count()
    response = client_reader.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
