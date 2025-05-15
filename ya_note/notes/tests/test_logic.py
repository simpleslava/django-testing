from http import HTTPStatus

from pytils.translit import slugify
from django.urls import reverse

from notes.models import Note
from .base_test_class import BaseTest


class TestNoteLogic(BaseTest):
    """Тестирование логики работы с заметками."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'New Note',
            'text': 'New Text',
            'slug': 'new-note'
        }
        cls.auto_slug_data = {
            'title': 'Автоматический слаг',
            'text': 'Текст заметки'
        }
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

    def test_logged_in_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.reader_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.filter(
            slug=self.form_data['slug'],
            author=self.reader
        ).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        initial_count = Note.objects.count()
        login_url = reverse('users:login')
        add_url = reverse('notes:add')
        response = self.client.post(add_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            response.url.startswith(f'{login_url}?next={add_url}')
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_count = Note.objects.count()
        duplicate_data = {
            'title': 'Another Note',
            'text': 'Another Text',
            'slug': self.note.slug,
            'author': self.author.id
        }
        response = self.author_client.post(
            reverse('notes:add'),
            data=duplicate_data
        )

        self.assertEqual(Note.objects.count(), initial_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('slug', response.context['form'].errors)

    def test_slug_autogeneration(self):
        """Slug автоматически генерируется из заголовка."""
        initial_count = Note.objects.count()
        response = self.author_client.post(
            reverse('notes:add'),
            data=self.auto_slug_data
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.filter(
            author=self.author
        ).order_by('-id').first()

        expected_slug = slugify(self.auto_slug_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        edit_url = reverse('notes:edit', args=[self.note.slug])
        response = self.author_client.post(edit_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        initial_count = Note.objects.count()
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.author_client.post(delete_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cannot_edit_note(self):
        """Читатель не может редактировать чужую заметку."""
        original_title = self.note.title
        edit_url = reverse('notes:edit', args=[self.note.slug])
        response = self.reader_client.post(edit_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, original_title)

    def test_reader_cannot_delete_note(self):
        """Читатель не может удалить чужую заметку."""
        initial_count = Note.objects.count()
        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.reader_client.post(delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
