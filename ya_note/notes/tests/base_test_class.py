from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.reader = User.objects.create_user(
            username='reader', password='password'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author,
        )
        cls.url_list = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_detail = reverse('notes:detail', args=[cls.note.slug])
        cls.url_edit = reverse('notes:edit', args=[cls.note.slug])
        cls.url_delete = reverse('notes:delete', args=[cls.note.slug])
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
