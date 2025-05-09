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
            username='author', password='pass'
        )
        cls.reader = User.objects.create_user(
            username='reader', password='pass'
        )
        cls.note = Note.objects.create(
            title='Test Note',
            text='Test Text',
            slug='test-note',
            author=cls.author,
        )

    def test_homepage_redirects_anonymous_to_login(self):
        login_url = reverse('users:login')
        url = reverse('notes:list')

        response = self.client.get(url)

        assert response.url == f'{login_url}?next={url}'

    def test_notes_pages_available_for_authenticated_user(self):
        urls = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
        ]
        self.client.force_login(self.author)

        for url in urls:
            response = self.client.get(url)
            assert response.status_code == HTTPStatus.OK

    def test_note_detail_and_modify_pages_available_only_for_author(self):
        urls = [
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]
        self.client.force_login(self.author)

        for url in urls:
            response = self.client.get(url)
            assert response.status_code == HTTPStatus.OK

    def test_auth_pages_available_for_all(self):
        pages = [
            ('get', reverse('users:login')),
            ('post', reverse('users:logout')),
            ('get', reverse('users:signup')),
        ]

        for method, url in pages:
            response = getattr(self.client, method)(url)
            assert response.status_code == HTTPStatus.OK

    def test_redirect_protected_pages_for_anonymous(self):
        login_url = reverse('users:login')
        urls = [
            reverse('notes:add'),
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.url.startswith(f'{login_url}?next=')
