import pytest
from django.conf import settings
from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count_on_homepage(client, many_news, home_url):
    """Проверка количества новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_homepage(client, many_news, home_url):
    """Проверка сортировки новостей на главной странице."""
    response = client.get(home_url)
    news_list = list(response.context['object_list'])
    sorted_news = sorted(news_list, key=lambda x: x.date, reverse=True)
    assert news_list == sorted_news


def test_comment_order_on_news_detail_page(client, news, comments, detail_url):
    """Проверка хронологического порядка комментариев."""
    response = client.get(detail_url)
    comment_list = list(response.context['news'].comment_set.all())
    assert comment_list == sorted(comments, key=lambda x: x.created)


def test_comment_form_not_bound_for_anonymous(client, detail_url):
    """Проверка отсутствия формы для анонимного пользователя."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_comment_form_available_for_author(client_author, detail_url):
    """Проверка наличия формы для авторизованного пользователя."""
    response = client_author.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
