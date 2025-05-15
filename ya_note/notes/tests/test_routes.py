from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='pass'
        )
        cls.note = Note.objects.create(
            title='Test Note',
            text='Test Text',
            slug='test-note',
            author=cls.author,
        )

        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.home_url = reverse('notes:home')

        cls.public_urls = (
            cls.login_url,
            cls.logout_url,
            cls.signup_url,
            cls.home_url
        )

        cls.auth_user_urls = (
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success')
        )

        cls.author_only_urls = (
            reverse('notes:detail', args=[cls.note.slug]),
            reverse('notes:edit', args=[cls.note.slug]),
            reverse('notes:delete', args=[cls.note.slug]),
        )

        cls.protected_urls = cls.auth_user_urls + cls.author_only_urls

    def test_public_pages_available_for_all(self):
        """Публичные страницы доступны всем."""
        for url in self.public_urls:
            with self.subTest(url=url):
                method = 'post' if url == self.logout_url else 'get'
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages(self):
        """Страницы для авторизованных пользователей доступны."""
        self.client.force_login(self.author)
        for url in self.auth_user_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages(self):
        """Страницы для автора заметки доступны."""
        self.client.force_login(self.author)
        for url in self.author_only_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_protected_pages_for_anonymous(self):
        """Защищенные страницы перенаправляют анонимного пользователя."""
        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertTrue(
                    response.url.startswith(f'{self.login_url}?next=')
                )

    def test_reader_cannot_access_author_pages(self):
        """Читатель не может получить доступ к страницам автора."""
        self.client.force_login(self.reader)
        for url in self.author_only_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
