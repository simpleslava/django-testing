from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
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
        cls.form_data = {
            'title': 'New Note',
            'text': 'New Text',
            'slug': 'new-note'
        }
        cls.url_list = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_detail = reverse('notes:detail', args=[cls.note.slug])
        cls.url_edit = reverse('notes:edit', args=[cls.note.slug])
        cls.url_delete = reverse('notes:delete', args=[cls.note.slug])
