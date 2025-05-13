import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Тестовый комментарий'


@pytest.fixture
def home_url():
    return reverse('news:home')


def test_news_count_on_homepage(client, many_news, home_url, settings):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_homepage(client, many_news, home_url):
    response = client.get(home_url)
    news_list = response.context['object_list']
    for i in range(len(news_list) - 1):
        assert news_list[i].date >= news_list[i + 1].date


def test_comment_order_on_news_detail_page(client, news, author):
    now = timezone.now()
    comments = [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment {i}',
            created=now - timedelta(days=i)
        )
        for i in range(3)
    ]
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    comment_list = list(response.context['news'].comment_set.all())
    assert comment_list == sorted(comments, key=lambda x: x.created)


def test_comment_form_not_bound_for_anonymous(client, news):
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert 'form' not in response.context


def test_comment_form_available_for_author(client_author, news):
    url = reverse('news:detail', args=[news.pk])
    response = client_author.get(url)
    assert 'form' in response.context
    from news.forms import CommentForm
    assert isinstance(response.context['form'], CommentForm)
