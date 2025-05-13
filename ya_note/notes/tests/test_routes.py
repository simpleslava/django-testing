from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


PUBLIC_URLS = [
    ('users:login', []),
    ('users:signup', []),
    ('users:logout', []),
]


AUTH_URLS = [
    ('notes:list', []),
    ('notes:add', []),
    ('notes:success', []),
]


AUTHOR_URLS = [
    ('notes:detail', ['note.slug']),
    ('notes:edit', ['note.slug']),
    ('notes:delete', ['note.slug']),
]


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

    def test_homepage_redirects_anonymous_to_login(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response.url,
            f'{self.login_url}?next={reverse("notes:list")}'
        )

    def test_auth_pages_available_for_all(self):
        for method, url in [
            ('get', self.login_url),
            ('post', self.logout_url),
            ('get', self.signup_url),
        ]:
            with self.subTest(url=url, method=method):
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages(self):
        self.client.force_login(self.author)
        for url in [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages(self):
        self.client.force_login(self.author)
        for url in [
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_protected_pages_for_anonymous(self):
        for url in [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertTrue(
                    response.url.startswith(f'{self.login_url}?next=')
                )
