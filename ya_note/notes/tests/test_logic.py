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

    def test_logged_in_user_can_create_note(self):
        form_data = {'title': 'New Note', 'text': 'New Text'}
        initial_count = Note.objects.count()
        self.client.force_login(self.reader)
        response = self.client.post(reverse('notes:add'), data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_anonymous_cannot_create_note(self):
        form_data = {'title': 'Anon Note', 'text': 'Anon Text'}
        initial_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=form_data)
        login_url = reverse('users:login')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            response.url.startswith(f'{login_url}?next={reverse("notes:add")}')
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_duplicate_slug(self):
        form_data = {
            'title': 'Another Note',
            'text': 'Another Text',
            'slug': self.note.slug,
        }
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=form_data)
        self.assertEqual(Note.objects.count(), initial_count)
        form = response.context.get('form')
        self.assertIn('slug', form.errors)

    def test_slug_autogeneration(self):
        form_data = {'title': 'Автоматический слаг', 'text': 'Text'}
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.get(title='Автоматический слаг')
        self.assertEqual(note.slug, 'avtomaticheskij-slag')

    def test_author_can_edit_note(self):
        form_data = {'title': 'Updated Note', 'text': 'Updated Text'}
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.post(url, data=form_data)
        self.note.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.text, 'Updated Text')

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_reader_cannot_edit_note(self):
        form_data = {'title': 'Hacked Note', 'text': 'Hacked Text'}
        initial_title = self.note.title
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.post(url, data=form_data)
        self.note.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.title, initial_title)

    def test_reader_cannot_delete_note(self):
        initial_count = Note.objects.count()
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
