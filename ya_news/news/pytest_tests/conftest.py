from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


EXTRA_NEWS = 5


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(
        username='author',
        password='pass'
    )


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(
        username='reader',
        password='pass'
    )


@pytest.fixture
def client_author(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def client_reader(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Test News',
        text='Test Text'
    )


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=[news.pk])


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=[comment.pk])


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    return [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment {i}',
            created=now - timedelta(days=i)
        )
        for i in range(3)
    ]


@pytest.fixture
def many_news(db):
    now = timezone.now()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=now - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + EXTRA_NEWS)
    )
