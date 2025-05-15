from notes.forms import NoteForm
from .base_test_class import BaseTest


class TestNoteContent(BaseTest):
    """Тестирование содержимого страниц, связанных с заметками."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

    def test_note_in_object_list(self):
        """Проверяет, что созданная заметка присутствует в списке."""
        response = self.author_client.get(self.url_list)
        self.assertIn(self.note, response.context['object_list'])

    def test_foreign_note_not_in_object_list(self):
        """Проверяет, что чужая заметка не отображается в списке."""
        response = self.reader_client.get(self.url_list)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_in_context(self):
        """Наличие формы в контексте страниц создания и редактирования."""
        urls = (self.url_add, self.url_edit)

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
