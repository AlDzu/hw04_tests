# Тесты моделей
# posts/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostsModelTest.group
        verbose = group.title
        self.assertEqual(verbose, str(group))
        self.assertEqual(verbose, 'Тестовая группа')
        verbose = group.slug
        self.assertEqual(verbose, 'Тестовый слаг')
        verbose = group.description
        self.assertEqual(verbose, 'Тестовое описание')

        post = PostsModelTest.post
        verbose = post.author.username
        self.assertEqual(verbose, 'auth')
        verbose = post.text
        self.assertEqual(verbose, 'Тестовая пост')
