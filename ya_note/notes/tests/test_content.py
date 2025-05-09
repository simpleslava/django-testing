from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteContent(TestCase):
    """Тестирование содержимого страниц, связанных с заметками."""
    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные: пользователей и одну заметку."""
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
        cls.url_edit = reverse('notes:edit', args=[cls.note.slug])

    def test_note_in_object_list(self):
        """Проверяет, что созданная заметка присутствует в списке."""
        self.client.force_login(self.author)

        response = self.client.get(self.url_list)

        assert self.note in response.context['object_list']

    def test_foreign_note_not_in_object_list(self):
        """Проверяет, что чужая заметка не отображается в списке."""
        self.client.force_login(self.reader)

        response = self.client.get(self.url_list)

        assert self.note not in response.context['object_list']

    def test_form_in_context(self):
        """Наличие формы в контексте страниц создания и редактирования."""
        self.client.force_login(self.author)
        urls = (self.url_add, self.url_edit)

        for url in urls:
            response = self.client.get(url)
            assert 'form' in response.context
            assert isinstance(response.context['form'], NoteForm)
