import pytest
from http import HTTPStatus
from pytest_lazyfixture import lazy_fixture


pytestmark = pytest.mark.django_db

public_urls = (
    lazy_fixture('home_url'),
    lazy_fixture('detail_url'),
    lazy_fixture('login_url'),
    lazy_fixture('signup_url')
)

private_urls = (
    lazy_fixture('edit_url'),
    lazy_fixture('delete_url')
)


def test_public_routes_available(client, *public_urls):
    """Проверка доступности публичных маршрутов."""
    for url in public_urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_private_routes_available(client_author, *private_urls):
    """Проверка доступности приватных маршрутов для автора."""
    for url in private_urls:
        response = client_author.get(url)
        assert response.status_code == HTTPStatus.OK


def test_redirect_anonymous_to_login(client, login_url, *private_urls):
    """Проверка редиректа анонимных пользователей на страницу входа."""
    for url in private_urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url.startswith(f'{login_url}?next=')


def test_reader_cannot_access_private(client_reader, *private_urls):
    """Проверка недоступности приватных маршрутов для других пользователей."""
    for url in private_urls:
        response = client_reader.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND


def test_logout_page_available_for_anonymous_post(client, logout_url):
    """Проверка доступности страницы выхода для POST-запросов."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
