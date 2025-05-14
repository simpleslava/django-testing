import pytest
from http import HTTPStatus


pytestmark = pytest.mark.django_db


def test_public_routes_available(
    client, home_url, detail_url, login_url, logout_url, signup_url
):
    """Проверка доступности публичных маршрутов."""
    urls = (home_url, detail_url, login_url, signup_url)
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_private_routes_available(client_author, edit_url, delete_url):
    """Проверка доступности приватных маршрутов для автора."""
    urls = (edit_url, delete_url)
    for url in urls:
        response = client_author.get(url)
        assert response.status_code == HTTPStatus.OK


def test_redirect_anonymous_to_login(client, edit_url, delete_url, login_url):
    """Проверка редиректа анонимных пользователей на страницу входа."""
    urls = (edit_url, delete_url)
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url.startswith(f'{login_url}?next=')


def test_reader_cannot_access_private(client_reader, edit_url, delete_url):
    """Проверка недоступности приватных маршрутов для других пользователей."""
    urls = (edit_url, delete_url)
    for url in urls:
        response = client_reader.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND


def test_logout_page_available_for_anonymous_post(client, logout_url):
    """Проверка доступности страницы выхода для POST-запросов."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
