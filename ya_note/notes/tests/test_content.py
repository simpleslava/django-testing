from notes.forms import NoteForm
from .base_test_class import BaseTest


class TestNoteContent(BaseTest):
    """Тестирование содержимого страниц, связанных с заметками."""

    def setUp(self):
        self.client.force_login(self.author)

    def test_note_in_object_list(self):
        """Проверяет, что созданная заметка присутствует в списке."""
        response = self.client.get(self.url_list)
        self.assertIn(self.note, response.context['object_list'])

    def test_foreign_note_not_in_object_list(self):
        """Проверяет, что чужая заметка не отображается в списке."""
        self.client.force_login(self.reader)
        response = self.client.get(self.url_list)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_in_context(self):
        """Наличие формы в контексте страниц создания и редактирования."""
        urls = (self.url_add, self.url_edit)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
