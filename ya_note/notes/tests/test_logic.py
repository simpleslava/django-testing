from http import HTTPStatus

from pytils.translit import slugify
from django.urls import reverse

from notes.models import Note
from .base_test_class import BaseTest


class TestNoteLogic(BaseTest):
    """Тестирование логики работы с заметками."""

    def test_logged_in_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        self.client.force_login(self.reader)
        response = self.client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.reader)

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        initial_count = Note.objects.count()
        login_url = reverse('users:login')
        response = self.client.post(self.url_add, data=self.form_data)
        self.assertRedirects(
            response,
            f'{login_url}?next={self.url_add}'
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(
            self.url_add,
            data={
                'title': 'Another Note',
                'text': 'Another Text',
                'slug': self.note.slug
            }
        )
        self.assertEqual(Note.objects.count(), initial_count)
        form = response.context['form']
        self.assertTrue(form.has_error('slug'))
        self.assertIn('уже существует', form.errors['slug'][0])

    def test_slug_autogeneration(self):
        """Slug автоматически генерируется из заголовка."""
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        form_data = {
            'title': 'Автоматический слаг',
            'text': 'Текст заметки'
        }
        response = self.client.post(self.url_add, data=form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get(title='Автоматический слаг')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        initial_count = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cannot_edit_note(self):
        """Читатель не может редактировать чужую заметку."""
        original_note = Note.objects.get(pk=self.note.pk)
        self.client.force_login(self.reader)
        response = self.client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, original_note.title)
        self.assertEqual(self.note.text, original_note.text)
        self.assertEqual(self.note.author, original_note.author)

    def test_reader_cannot_delete_note(self):
        """Читатель не может удалить чужую заметку."""
        initial_count = Note.objects.count()
        self.client.force_login(self.reader)
        response = self.client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
