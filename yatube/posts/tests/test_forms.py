# Тесты форм
# posts/tests/test_forms.py
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

URL_POST_CREATE = reverse('posts:post_create')


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
        self.URL_PROFILE = reverse(
            'posts:profile', kwargs={'username': self.user.username}
        )

    def test_create_post(self):
        """Тест создания нового поста при отправке формы"""
        posts_count = Post.objects.count()
        form_data = {
            'group': {self.group.id},
            'text': 'Тестовый текст',
        }
        response = self.autorized_author.post(
            URL_POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.URL_PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст',
                author=self.user,
            ).exists()
        )
        self.assertNotEqual(
            ((response.context.get('page_obj').object_list)[0]).id, posts_count
        )  # проверка что ид последнего поста равен количеству, т.е. последний?

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
            URL_POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.URL_PROFILE)
        old_post = Post.objects.get(
            id=((response.context.get('page_obj').object_list)[0]).id
        )
        URL_EDIT_POST = reverse(
            'posts:post_edit', kwargs={'post_id': old_post.id}
        )
        response = self.autorized_author.post(
            URL_EDIT_POST,
            data=edit_form_data,
            follow=True
        )
        new_post = Post.objects.get(id=old_post.id)
        self.assertNotEqual(old_post.text, new_post.text)
