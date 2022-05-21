# Тесты представлений
# posts/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse

from posts.settings import NUMBER_OF_POSTS
from posts.views import Group, Post, PostForm, User

URL_INDEX = reverse('posts:index')
URL_CREATE_POST = reverse('posts:post_create')


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.autorized_author = Client()
        cls.autorized_author.force_login(cls.user)
        cls.URL_PROFILE = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
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
        cls.URL_POSTS_GROUP = reverse(
            'posts:group', kwargs={'slug': cls.group.slug}
        )
        cls.URL_POSTS_GROUP_2 = reverse(
            'posts:group', kwargs={'slug': cls.group2.slug}
        )

        objs = (Post(
            text='Тестовый текст %s' % i, author=cls.user, group=cls.group
        ) for i in range(1, 12)
        )
        bulk_data = list(objs)
        Post.objects.bulk_create(bulk_data)
        cls.post = Post.objects.get(id=1)
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
        cls.URL_POST_DETAIL = reverse(
            'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}
        )
        cls.URL_POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}
        )

    def test_index_true_template(self):
        """Урл использует верный шаблон"""
        templates_pages_names = {
            'posts/index.html': URL_INDEX,
            'posts/group_list.html': self.URL_POSTS_GROUP,
            'posts/profile.html': self.URL_PROFILE,
            'posts/post_detail.html': self.URL_POST_DETAIL,
            'posts/create_post.html': URL_CREATE_POST,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.autorized_author.get(self.URL_POST_EDIT)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_true_index(self):
        """Главная страница"""
        response = self.autorized_author.get(URL_INDEX)
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)
        response = self.autorized_author.get(
            URL_INDEX + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_true_group_posts(self):
        """Посты по группам + пагинатор"""
        response = self.autorized_author.get(self.URL_POSTS_GROUP)
        self.assertEqual(response.context.get(
            'group').title, 'Тестовый заголовок')
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)
        response = self.autorized_author.get(
            self.URL_POSTS_GROUP + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_true_user_posts(self):
        """Посты по пользователю"""
        response = self.autorized_author.get(self.URL_PROFILE)
        self.assertEqual(
            response.context.get('user_info').username, self.user.username
        )
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)
        response = self.autorized_author.get(
            self.URL_PROFILE + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_true_id_post(self):
        """Пост по ид"""
        response = self.autorized_author.get(self.URL_POST_DETAIL)
        self.assertEqual(
            response.context.get('selected_post').text,
            f'Тестовый текст {self.post.id}'
        )

    def test_true_edit_post(self):
        """Форма редактирования поста по ид"""
        response = self.autorized_author.get(self.URL_POST_EDIT)
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)
        post_field = response.context.get('post')
        self.assertIsInstance(post_field, Post)

    def test_true_create_post(self):
        """Создание поста"""
        response = self.autorized_author.get(URL_CREATE_POST)
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)

    def test_new_post(self):
        """Тест нового поста"""
        response_index = self.autorized_author.get(URL_INDEX)
        last_post = (response_index.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился на главной
        response_group = self.autorized_author.get(self.URL_POSTS_GROUP)
        last_post = (response_group.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился в группах
        response_profile = self.autorized_author.get(self.URL_PROFILE)
        last_post = (response_profile.context.get('page_obj').object_list)[0]
        # последний пост
        self.assertEqual(last_post, self.post2)
        # Появился в профиле
        response_group2 = self.autorized_author.get(self.URL_POSTS_GROUP_2)
        last_post = (response_group2.context.get('page_obj').object_list)[0]
        # последний пост в группе 2
        self.assertNotEqual(last_post, self.post2)
        # Пост группы 1 Не появился в группе 2
        self.assertEqual(last_post, self.post3)
        # Появился в группе 1
