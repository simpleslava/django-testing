from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteLogic(TestCase):
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

    def test_logged_in_user_can_create_note(self):
        form_data = {'title': 'New Note', 'text': 'New Text'}
        self.client.force_login(self.reader)

        response = self.client.post(reverse('notes:add'), data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_anonymous_cannot_create_note(self):
        form_data = {'title': 'Anon Note', 'text': 'Anon Text'}

        response = self.client.post(reverse('notes:add'), data=form_data)

        login_url = reverse('users:login')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            response.url.startswith(f'{login_url}?next={reverse("notes:add")}')
        )

    def test_duplicate(self):
        form_data = {
            'title': 'Another Note',
            'text': 'Another Text',
            'slug': self.note.slug,
        }
        self.client.force_login(self.author)

        response = self.client.post(reverse('notes:add'), data=form_data)

        form = response.context.get('form')
        self.assertIn('slug', form.errors)

    def test_slug_autogeneration(self):
        form_data = {'title': 'Автоматический слаг', 'text': 'Text'}
        self.client.force_login(self.author)

        self.client.post(reverse('notes:add'), data=form_data)

        note = Note.objects.get(title='Автоматический слаг')
        self.assertEqual(note.slug, 'avtomaticheskij-slag')

    def test_modify_pages_access(self):
        cases = [
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        ]
        urls = [
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]

        for user, expected in cases:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                for url in urls:
                    with self.subTest(url=url):
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, expected)
