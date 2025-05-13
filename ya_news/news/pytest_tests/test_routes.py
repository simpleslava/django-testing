from http import HTTPStatus
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

PUBLIC_URLS = [
    ('news:home', []),
    ('news:detail', ['news.pk']),
    ('users:login', []),
    ('users:signup', []),
]

PRIVATE_URLS = [
    ('news:edit', ['comment.pk']),
    ('news:delete', ['comment.pk']),
]


@pytest.fixture
def urls(news, comment):
    return {
        'news.pk': news.pk,
        'comment.pk': comment.pk,
    }


@pytest.mark.parametrize('url_name,args', PUBLIC_URLS)
def test_public_routes_available(client, url_name, args, urls):
    resolved_args = [urls[arg] for arg in args]
    url = reverse(url_name, args=resolved_args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name,args', PRIVATE_URLS)
def test_private_routes_available(client_author, url_name, args, urls):
    resolved_args = [urls[arg] for arg in args]
    url = reverse(url_name, args=resolved_args)
    response = client_author.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name,args', PRIVATE_URLS)
def test_redirect_anonymous_to_login(client, url_name, args, urls):
    resolved_args = [urls[arg] for arg in args]
    url = reverse(url_name, args=resolved_args)
    login_url = reverse('users:login')
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(f'{login_url}?next=')


@pytest.mark.parametrize('url_name,args', PRIVATE_URLS)
def test_reader_cannot_access_private(client_reader, url_name, args, urls):
    resolved_args = [urls[arg] for arg in args]
    url = reverse(url_name, args=resolved_args)
    response = client_reader.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_logout_page_available_for_anonymous_post(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
