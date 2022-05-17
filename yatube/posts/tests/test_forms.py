# Тесты форм
# posts/tests/test_forms.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='Author')
        self.autorized_author = Client()
        self.autorized_author.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Тестовое описание'
        )

    def test_create_post(self):
        """Тест создания нового поста при отправке формы"""
        posts_count = Post.objects.count()
        form_data = {
            'group': f'{self.group.id}',
            'text': 'Тестовый текст',
        }
        response = self.autorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Author'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст',
                author=self.user,
            ).exists()
        )

    def test_edit_post(self):
        """Тест изменения поста при отправке формы"""
        form_data = {
            'group': f'{self.group.id}',
            'text': 'Тестовый текст',
        }
        edit_form_data = {
            'group': f'{self.group.id}',
            'text': 'Изменённый Тестовый текст',
        }
        response = self.autorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Author'})
        )
        old_post = Post.objects.get(id=1)
        response = self.autorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': old_post.id}),
            data=edit_form_data,
            follow=True
        )
        new_post = Post.objects.get(id=1)
        self.assertNotEqual(old_post.text, new_post.text)
