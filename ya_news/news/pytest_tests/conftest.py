from datetime import timedelta

import pytest
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Создаёт пользователя-автора."""
    return django_user_model.objects.create_user(
        username='author', password='pass'
    )


@pytest.fixture
def reader(django_user_model):
    """Создаёт пользователя-читателя."""
    return django_user_model.objects.create_user(
        username='reader', password='pass'
    )


@pytest.fixture
def client_author(author, client):
    """Возвращает клиента, залогиненного как автор."""
    client.force_login(author)
    return client


@pytest.fixture
def client_reader(reader, client):
    """Возвращает клиента, залогиненного как читатель."""
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    """Создаёт одиночную новость для тестирования."""
    return News.objects.create(title='Test News', text='Test Text')


@pytest.fixture
def comment(db, news, author):
    """Создаёт одиночный комментарий для тестирования."""
    return Comment.objects.create(
        news=news, author=author, text='Test comment'
    )


@pytest.fixture
def many_news(db):
    """Создаёт пятнадцать новостей для проверки лимита на главной странице."""
    return News.objects.bulk_create(
        [
            News(title=f'Новость {index}', text='Текст новости')
            for index in range(15)
        ]
    )


@pytest.fixture
def ordered_news(db):
    """Создаёт три новости для проверки порядка: новая, средняя и старая."""
    now = timezone.now()
    old = News.objects.create(
        title='Старая новость', text='...', date=now - timedelta(days=2)
    )
    mid = News.objects.create(
        title='Средняя новость', text='...', date=now - timedelta(days=1)
    )
    new = News.objects.create(title='Новая новость', text='...', date=now)
    return [new, mid, old]


@pytest.fixture
def ordered_comments(db, news, author):
    """Создаёт три комментария в порядке даты создания."""
    now = timezone.now()
    old_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Старый',
        created=now - timedelta(days=2),
    )
    mid_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Средний',
        created=now - timedelta(days=1),
    )
    new_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Новый',
        created=now,
    )
    return [old_comment, mid_comment, new_comment]
