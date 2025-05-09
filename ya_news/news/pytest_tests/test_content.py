import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_news_count_on_homepage(client, many_news):
    """На главной выводится не более десяти новостей."""
    url = reverse('news:home')
    response = client.get(url)
    assert len(response.context['object_list']) <= 10


def test_news_order_on_homepage(client, ordered_news):
    """Новости на главной странице сортируются в правильном порядке."""
    url = reverse('news:home')
    response = client.get(url)
    assert list(response.context['object_list']) == ordered_news


def test_comment_order_on_news_detail_page(client, ordered_comments):
    """Комментарии на странице новости отображаются в порядке записи."""
    first_pk = ordered_comments[0].news.pk
    url = reverse('news:detail', args=[first_pk])
    response = client.get(url)
    assert list(response.context['news'].comment_set.all()) == ordered_comments


def test_comment_form_not_bound_for_anonymous(client, news):
    """Анонимному пользователю форма комментария не передаётся в контекст."""
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.context.get('form') is None


def test_comment_form_available_for_author(client_author, news):
    """Авторизованному пользователю форма комментария доступна."""
    url = reverse('news:detail', args=[news.pk])
    response = client_author.get(url)
    assert response.context.get('form') is not None
