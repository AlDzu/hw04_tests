# Тесты адресов
# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.autorized_author = Client()
        cls.autorized_author.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.autorized_client = Client()
        self.autorized_client.force_login(self.user)

    def test_posts_urls(self):
        """Доступность урлов posts"""

        urls_templates_all = {
            '': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html'
        }
        urls_templates_autorised = {
            '/create/': 'posts/create_post.html'
        }
        urls_templates_author = {
            '/posts/1/edit/': 'posts/create_post.html'
        }

        for url, template in urls_templates_all.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
                response = self.autorized_client.get(url)
                self.assertTemplateUsed(response, template)

        for url, template in urls_templates_autorised.items():
            with self.subTest(url=url):
                response = self.autorized_client.get(url)
                self.assertTemplateUsed(response, template)

        for url, template in urls_templates_author.items():
            with self.subTest(url=url):
                response = self.autorized_author.get(url)
                self.assertTemplateUsed(response, template)
