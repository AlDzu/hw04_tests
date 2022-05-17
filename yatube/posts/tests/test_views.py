# Тесты представлений
# posts/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.views import Group, Post, PostForm

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.autorized_author = Client()
        cls.autorized_author.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test2',
            description='Тестовое описание2'
        )
        for i in range(1, 12):
            cls.post = Post.objects.create(
                text=(f'Тестовый текст {i}'),
                author=cls.user,
                group=cls.group,
            )
        cls.post3 = Post.objects.create(
            text='Тестовый текст группы два',
            author=cls.user,
            group=cls.group2,
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст последнего поста',
            author=cls.user,
            group=cls.group,
        )

    def test_index_true_template(self):
        """Урл использует верный шаблон"""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group',
                kwargs={'slug': 'test'}),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'Author'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}),
            'posts/create_post.html': reverse(
                'posts:post_create'),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_true_index(self):
        """Главная страница"""
        response = self.autorized_author.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.autorized_author.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_true_group_posts(self):
        """Посты по группам + пагинатор"""
        response = self.autorized_author.get(
            reverse('posts:group', kwargs={'slug': 'test'}))
        self.assertEqual(response.context.get(
            'group').title, 'Тестовый заголовок')
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.autorized_author.get(
            reverse('posts:group', kwargs={'slug': 'test'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_true_user_posts(self):
        """Посты по пользователю"""
        response = self.autorized_author.get(
            reverse('posts:profile', kwargs={'username': 'Author'}))
        self.assertEqual(response.context.get('user_info').username, 'Author')
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.autorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'Author'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_true_id_post(self):
        """Пост по ид"""
        response = self.autorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(
            response.context.get('selected_post').text,
            f'Тестовый текст {self.post.id}')

    def test_true_edit_post(self):
        """Форма редактирования поста по ид"""
        response = self.autorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)
        post_field = response.context.get('post')
        self.assertIsInstance(post_field, Post)

    def test_true_create_post(self):
        """Создание поста"""
        response = self.autorized_author.get(reverse('posts:post_create'))
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)

    def test_new_post(self):
        """Тест нового поста"""
        response_index = self.autorized_author.get(reverse('posts:index'))
        last_post = (response_index.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился на главной
        response_group = self.autorized_author.get(reverse(
            'posts:group',
            kwargs={'slug': 'test'}))
        last_post = (response_group.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился в группах
        response_profile = self.autorized_author.get(reverse(
            'posts:profile',
            kwargs={'username': 'Author'}))
        last_post = (response_profile.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился в профиле
        response_group2 = self.autorized_author.get(reverse(
            'posts:group',
            kwargs={'slug': 'test2'}))
        last_post = (response_group2.context.get('page_obj').object_list)[0]
        # последний пост в группе 2
        self.assertNotEqual(last_post, self.post2)
        # Пост группы 1 Не появился в группе 2
        self.assertEqual(last_post, self.post3)
        # Появился в группе 1
