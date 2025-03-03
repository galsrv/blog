from http import HTTPStatus
from django.contrib.auth import get_user, get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.models import Blog, Blogger, Comment

User = get_user_model()

USERNAME1 = 'test_user1'
USERNAME2 = 'test_user2'
USERNAME3 = 'test_user3'
PASSWORD = 'Userpass1'
BULK_TITLE = 'Blog title '
BULK_CONTENT = 'Blog content '
BULK_AMOUNT = 100
BULK_BATCH = 10
TITLE = 'Test title'
CONTENT = 'Test content'
ID_TO_TEST = 111
EDITED_TITLE_SUFFIX = ' edited'
EDITED_CONTENT_SUFFIX = ' edited'
COMMENT_TEXT = 'This is a comment'
BIO = 'blabla'
BIO_TO_TEST = 'test bio'
TEST_AVATAR = 'test_avatar.png'
TEST_IMAGE = 'test_image.png'
NUMBER_OF_TEST_USERS = 2


class TestAPIBlogs(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username=USERNAME1, password=PASSWORD)
        self.user2 = User.objects.create_user(username=USERNAME2, password=PASSWORD)
        Blogger.objects.create(user=self.user1, bio=BIO)
        Blogger.objects.create(user=self.user2, bio=BIO)
        self.blogs = (Blog(
            title=BULK_TITLE+str(i),
            content=BULK_CONTENT+str(i),
            author=self.user1) for i in range(BULK_AMOUNT))
        Blog.objects.bulk_create(self.blogs, BULK_BATCH)

    def test_signup(self):
        ''' Создание юзера. Проверяем, что 
        - Пользователя изначально не было
        - Пользователь появился 
        - Ответ 201
        '''
        self.assertFalse(User.objects.filter(username=USERNAME3).exists())
        response = self.client.post(reverse('user-list'), {'username': USERNAME3, 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(User.objects.filter(username=USERNAME3).exists())

    def test_user_login_logout(self):
        ''' Логин и логаут юзера. Проверяем, что 
        - Логин. Ответ 200
        - Логин. Ответ включает auth_token
        - Логаут. Ответ 204
        '''
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('auth_token', response.data.keys())

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.post(reverse('logout'), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_blogs_list(self):
        ''' Список записей. Проверяем, что 
        - Аноним и авторизованный пользователь имеют доступ к данным
        - Ответ 200
        - Ответ содержит верное число записей
        '''
        # Аноним
        response = self.client.get(reverse('blog-list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['count'], BULK_AMOUNT)
        self.assertIn('results', response.data.keys())

        # Авторизованный пользователь 
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.get(reverse('blog-list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['count'], BULK_AMOUNT)
        self.assertIn('results', response.data.keys())

    def test_blog_details(self):
        ''' Отдельная запись. Проверяем, что 
        - Аноним и авторизованный пользователь имеют доступ к данным
        - Ответ 200
        - Ответ содержит требуемые поля
        - Значения полей верны
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        # Аноним
        response = self.client.get(reverse('blog-detail', kwargs={'pk': blog.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertIn('author', response.data.keys())
        self.assertEqual(blog.title, response.data['title'])
        self.assertEqual(blog.content, response.data['content'])
        self.assertEqual(blog.author.id, response.data['author'])

        # Авторизованный пользователь 
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.get(reverse('blog-detail', kwargs={'pk': blog.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertIn('author', response.data.keys())
        self.assertEqual(blog.title, response.data['title'])
        self.assertEqual(blog.content, response.data['content'])
        self.assertEqual(blog.author.id, response.data['author'])

    def test_blog_create(self):
        ''' Создание записи. Проверяем, что 
        - Аноним получает 403
        - Авторизованный пользователь получает 201
        - Ответ содержит требуемые поля
        - Значения полей верны
        '''
        # Аноним
        response = self.client.post(reverse('blog-list'), {'title': TITLE, 'content': CONTENT}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Авторизованный пользователь
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.post(reverse('blog-list'), {'title': TITLE, 'content': CONTENT}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertIn('author', response.data.keys())
        self.assertEqual(TITLE, response.data['title'])
        self.assertEqual(CONTENT, response.data['content'])
        self.assertEqual(User.objects.get(username=USERNAME1).id, response.data['author'])

    def test_blog_update(self):
        ''' Редактирование записи. Проверяем, что 
        - Аноним получает 401
        - Неавтор получает 403
        - Автор получает 200
        - Значения полей изменились
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        # Аноним
        response = self.client.put(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX, 'content': CONTENT + EDITED_CONTENT_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        blog.refresh_from_db()
        self.assertEqual(blog.title, TITLE)
        self.assertEqual(blog.content, CONTENT)

        # Неавтор
        response = self.client.post(reverse('login'), {'username': USERNAME2, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.put(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX, 'content': CONTENT + EDITED_CONTENT_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        blog.refresh_from_db()
        self.assertEqual(blog.title, TITLE)
        self.assertEqual(blog.content, CONTENT)

        # Автор
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.put(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX, 'content': CONTENT + EDITED_CONTENT_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertEqual(TITLE + EDITED_TITLE_SUFFIX, response.data['title'])
        self.assertEqual(CONTENT + EDITED_CONTENT_SUFFIX, response.data['content'])

    def test_blog_partial_update(self):
        ''' Редактирование отдельных полей записи. Проверяем, что 
        - Аноним получает 401
        - Неавтор получает 403
        - Автор получает 200
        - Значения нужных полей изменились
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        # Аноним
        response = self.client.patch(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        blog.refresh_from_db()
        self.assertEqual(blog.title, TITLE)
        self.assertEqual(blog.content, CONTENT)

        # Неавтор
        response = self.client.post(reverse('login'), {'username': USERNAME2, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.patch(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        blog.refresh_from_db()
        self.assertEqual(blog.title, TITLE)
        self.assertEqual(blog.content, CONTENT)

        # Автор
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.patch(reverse('blog-detail', kwargs={'pk': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertEqual(TITLE + EDITED_TITLE_SUFFIX, response.data['title'])
        self.assertEqual(CONTENT, response.data['content'])

    def test_blog_delete(self):
        ''' Удаление записи. Проверяем, что 
        - Аноним получает 401
        - Неавтор получает 403
        - Автор получает 200
        - Значения нужных полей изменились
        '''

        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        # Аноним
        response = self.client.delete(reverse('blog-detail', kwargs={'pk': blog.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertTrue(Blog.objects.filter(title=TITLE).exists())

        # Неавтор
        response = self.client.post(reverse('login'), {'username': USERNAME2, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.delete(reverse('blog-detail', kwargs={'pk': blog.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Blog.objects.filter(title=TITLE).exists())

        # Автор
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.delete(reverse('blog-detail', kwargs={'pk': blog.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Blog.objects.filter(title=TITLE).exists())

    def test_comment_create(self):
        ''' Создание комментария. Проверяем, что 
        - Аноним получает 403
        - Авторизованный пользователь получает 201
        - Ответ содержит требуемые поля
        - Значения полей верны
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        # Аноним
        response = self.client.post(reverse('blog-comment', kwargs={'pk': blog.id}), {'text': COMMENT_TEXT}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Авторизованный пользователь
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.post(reverse('blog-comment', kwargs={'pk': blog.id}), {'text': COMMENT_TEXT}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn('title', response.data.keys())
        self.assertIn('content', response.data.keys())
        self.assertIn('author', response.data.keys())
        self.assertIn('comments', response.data.keys())
        self.assertEqual(response.data['comments'][0]['text'], COMMENT_TEXT)

    def test_comment_delete(self):
        ''' Удаление комментария. Проверяем, что 
        - Аноним получает 401
        - Неавтор получает 403
        - Автор получает 200
        - Запись удалена
        '''

        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        comment = Comment(to_blog=blog, text=COMMENT_TEXT, author=self.user1)
        comment.save()

        # Аноним
        response = self.client.delete(reverse('api-comment-delete', kwargs={'id': blog.id, 'comment_id': comment.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(text=COMMENT_TEXT).exists())

        # Неавтор
        response = self.client.post(reverse('login'), {'username': USERNAME2, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.delete(reverse('api-comment-delete', kwargs={'id': blog.id, 'comment_id': comment.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Comment.objects.filter(text=COMMENT_TEXT).exists())

        # Автор
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.delete(reverse('api-comment-delete', kwargs={'id': blog.id, 'comment_id': comment.id}), {}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Comment.objects.filter(text=COMMENT_TEXT).exists())

    def test_bloggers_list(self):
        ''' Список блоггеров. Проверяем, что 
        - Аноним и авторизованный пользователь имеют доступ к данным
        - Ответ 200
        - Ответ содержит верное число записей
        '''
        # Аноним
        response = self.client.get(reverse('api-bloggers-list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), NUMBER_OF_TEST_USERS)

        # Авторизованный пользователь 
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.get(reverse('api-bloggers-list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), NUMBER_OF_TEST_USERS)

    def test_bloggers_details(self):
        ''' Отдельная запись блоггера. Проверяем, что 
        - Аноним и авторизованный пользователь имеют доступ к данным
        - Ответ 200
        - Ответ содержит требуемые поля
        - Значения полей верны
        '''
        user = User.objects.get(username=USERNAME1)

        # Аноним
        response = self.client.get(reverse('api-bloggers-detail', kwargs={'id': user.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('username', response.data.keys())
        self.assertIn('blogger', response.data.keys())
        self.assertIn('blogs', response.data.keys())
        self.assertEqual(USERNAME1, response.data['username'])
        self.assertEqual(BIO, response.data['blogger']['bio'])

        # Авторизованный пользователь 
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.get(reverse('api-bloggers-detail', kwargs={'id': user.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('username', response.data.keys())
        self.assertIn('blogger', response.data.keys())
        self.assertIn('blogs', response.data.keys())
        self.assertEqual(USERNAME1, response.data['username'])
        self.assertEqual(BIO, response.data['blogger']['bio'])

    def test_blogger_profile(self):
        ''' Редактирование отдельных полей записи блоггера. Проверяем, что 
        - Аноним получает 401
        - Посторонний пользователь получает 403
        - Сам пользователь получает 200
        - Значения нужных полей изменились
        '''
        user = User.objects.get(username=USERNAME1)

        # Аноним
        response = self.client.patch(reverse('api-bloggers-profile', kwargs={'id': user.id}), {'bio': BIO_TO_TEST}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(user.blogger.bio, BIO)

        # Посторонний пользователь
        response = self.client.post(reverse('login'), {'username': USERNAME2, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        response = self.client.patch(reverse('api-bloggers-profile', kwargs={'id': user.id}), {'bio': BIO_TO_TEST}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(user.blogger.bio, BIO)

        # Сам пользователь
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])

        with open('media/' + TEST_AVATAR, 'rb') as image_file:
            # Внимание, другой формат запроса
            response = self.client.patch(reverse('api-bloggers-profile', kwargs={'id': user.id}), {'bio': BIO_TO_TEST, 'avatar': image_file}, format='multipart')
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('username', response.data.keys())
            self.assertIn('blogger', response.data.keys())
            self.assertIn('blogs', response.data.keys())
            self.assertEqual(USERNAME1, response.data['username'])
            self.assertEqual(BIO_TO_TEST, response.data['blogger']['bio'])
            user.refresh_from_db()
            self.assertEqual(user.blogger.avatar, 'avatars/' + TEST_AVATAR)

            blogger = user.blogger
            blogger.avatar.delete()


