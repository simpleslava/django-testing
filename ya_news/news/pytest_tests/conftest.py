from datetime import timedelta
import pytest
from django.utils import timezone
from news.models import Comment, News

NEWS_COUNT = 10
EXTRA_NEWS = 5


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(
        username='author', password='pass'
    )


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        username='reader', password='pass'
    )


@pytest.fixture
def client_author(author):
    from django.test import Client
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def client_reader(reader):
    from django.test import Client
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Test News', text='Test Text')


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news, author=author, text='Test comment'
    )


@pytest.fixture
def many_news(db):
    now = timezone.now()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=now - timedelta(days=index)
        )
        for index in range(NEWS_COUNT + EXTRA_NEWS)
    )
