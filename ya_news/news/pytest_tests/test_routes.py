from http import HTTPStatus

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name,args,client_fixture,expected_status',
    [
        ('news:home', [], 'client', HTTPStatus.OK),
        ('news:detail', ['news.pk'], 'client', HTTPStatus.OK),
        ('news:edit', ['comment.pk'], 'client_author', HTTPStatus.OK),
        ('news:delete', ['comment.pk'], 'client_author', HTTPStatus.OK),
    ],
)
def test_get_routes(
    request, url_name, args, client_fixture, expected_status, news, comment
):
    """Проверяет доступность маршрутов с ожидаемым статусом."""
    lookup = {'news.pk': news.pk, 'comment.pk': comment.pk}
    resolved_args = [lookup[arg_key] for arg_key in args]
    url = reverse(url_name, args=resolved_args)
    response = request.getfixturevalue(client_fixture).get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_redirect_anonymous_to_login_on_modify(client, comment, url_name):
    """Редирект анонима на логин при попытке изменить или удалить."""
    url = reverse(url_name, args=[comment.pk])
    login_url = reverse('users:login')
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(f'{login_url}?next=')


@pytest.mark.parametrize('url_name', ['users:login', 'users:signup'])
def test_auth_pages_available_for_anonymous_get(client, url_name):
    """Проверяет доступность страниц логина и регистрации для анонимных."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_page_available_for_anonymous_post(client):
    """Проверяет доступность страницы выхода методом POST для анонимных."""
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
