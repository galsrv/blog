from http import HTTPStatus
from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Blog, Blogger, Comment

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


class TestBlogs(TestCase):
    
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
        1) GET ответ 200
        2) GET рендерится верный шаблон 
        3) GET определяется верный url 
        4) GET в контексте есть форма 
        5) POST ответ 200 после редиректа
        6) POST рендерится верный шаблон
        7) POST определяется верный url
        8) пользователь фактически создан
        9) залогиненного пользователя отправляет на главную - не стал делать через классы, нет контроля
        '''
        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/signup')
        self.assertIn('form', response.context.keys())

        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.post(reverse('signup'), {'username': USERNAME3, 'password1': PASSWORD, 'password2': PASSWORD,'bio': 'blabla'}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(response.redirect_chain, [('/accounts/login/', HTTPStatus.FOUND)])
        self.assertTrue(User.objects.filter(username=USERNAME3).exists())

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated) 

        response = self.client.get(reverse('signup'), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/signup')

    def test_user_login(self):
        ''' Логин юзера. Проверяем, что 
        1) GET ответ 200
        2) GET рендерится верный шаблон 
        3) GET определяется верный url 
        4) GET в контексте есть форма для логина
        5) POST ответ 200 после редиректа
        6) POST рендерится верный шаблон
        7) POST определяется верный url
        8) пользователь фактически залогинен
        '''
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertIn('form', response.context.keys())

        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.post(reverse('login'), {'username': USERNAME1, 'password': PASSWORD}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('index.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/')
        self.assertEqual(response.redirect_chain, [('/', HTTPStatus.FOUND)])
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_user_logout(self):
        ''' Логин юзера. Проверяем, что 
        1) GET ответ 200
        2) GET рендерится верный шаблон 
        3) GET определяется верный url 
        4) пользователь фактически разлогинен
        '''
        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('index.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/')
        self.assertEqual(response.redirect_chain, [('/', HTTPStatus.FOUND)])
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_blogs_list(self):
        ''' Список записей. Проверяем, что 
        1) возвращается верный статус страницы
        2) используется верный шаблон страницы 
        3) определяется верный url 
        4) выводится нужное число объектов на странице и подсчитывается верное число страниц 
        Сначала от имени анонима, потом от имени залогиненого юзера
        '''
        for _ in range(2):
            response = self.client.get(reverse('blogs_list'))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('blogs_list.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], '/blogs/')
            self.assertEqual(len(response.context['page_obj']), 5)
            self.assertEqual(response.context['num_pages'], 20)

            self.client.login(username=USERNAME1, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)

    def test_blog_details(self):
        ''' Отдельная запись. Проверяем, что 
        1) GET возвращается верный статус страницы
        2) GET используется верный шаблон страницы 
        3) GET определяется верный url 
        4) GET данные в контексте верны
        5) GET в контексте для залогиненного пользователя есть форма комментария
        Сначала от имени анонима, потом от имени залогиненого юзера
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        for _ in range(2):
            response = self.client.get(reverse('blog_details', kwargs={'blog_id': blog.id}))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('blog_details.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/')
            self.assertEqual(response.context['blog'].title, blog.title)

            self.client.login(username=USERNAME1, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)

        self.assertIn('comment_form', response.context.keys())

    def test_blog_create(self):
        ''' Создание записи. Проверяем, что 
        GET/POST анонима редиректим на страницу логина
        GET ответ 200, верный шаблон, верный url
        GET в контексте есть форма для поста
        POST ответ 200 после редиректа, верный шаблон, верный url
        POST данные в контексте верны
        POST в контексте есть форма для комментария
        POST запись содержит ссылку на файл картинки
        '''
        response = self.client.get(reverse('blog_create'), follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/blog/create/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)

        response = self.client.post(reverse('blog_create'), {'title': TITLE, 'content': CONTENT}, follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/blog/create/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
        self.assertTemplateUsed(response, 'form.html')

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('blog_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'form.html')
        self.assertEqual(response.request['PATH_INFO'], '/blog/create/')
        self.assertIn('form', response.context.keys())

        with open('media/' + TEST_IMAGE, 'rb') as image_file:
            response = self.client.post(reverse('blog_create'), {'title': TITLE, 'content': CONTENT, 'image': image_file}, follow=True)
            blog = Blog.objects.get(title=TITLE)

            self.assertRedirects(response, f'/blog/{blog.id}/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
            self.assertTemplateUsed(response, 'blog_details.html')
            
            self.assertEqual(response.context['blog'].title, blog.title)
            self.assertIn('comment_form', response.context.keys())
            self.assertEqual(blog.image, 'images/' + TEST_IMAGE)

            blog.image.delete()

    def test_blog_edit(self):
        ''' Редактирование записи. Проверяем, что 
        GET/POST анонима и неавтора редиректим на страницу поста
        GET автора ответ 200, верный шаблон, верный url
        GET в контексте есть форма для редактирования поста
        POST автора ответ 200 после редиректа, верный шаблон, верный url
        POST автора данные в контексте верны
        POST данные в БД верны после апдейта 
        POST в контексте есть форма для комментария
        POST запись содержит ссылку на файл картинки
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        for _ in range(2):
            response = self.client.get(reverse('blog_edit', kwargs={'blog_id': blog.id}), follow=True)
            self.assertRedirects(response, f'/blog/{blog.id}/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
            self.assertTemplateUsed(response, 'blog_details.html')

            response = self.client.post(reverse('blog_edit', kwargs={'blog_id': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX, 'content': CONTENT + EDITED_CONTENT_SUFFIX}, follow=True)
            self.assertRedirects(response, f'/blog/{blog.id}/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
            self.assertTemplateUsed(response, 'blog_details.html')

            self.assertEqual(blog.title, TITLE)
            self.assertEqual(blog.content, CONTENT)

            self.client.login(username=USERNAME2, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)   
        
        self.client.logout()

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('blog_edit', kwargs={'blog_id': blog.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/edit/')
        self.assertTemplateUsed(response, 'form.html')
        self.assertIn('form', response.context.keys())

        with open('media/' + TEST_IMAGE, 'rb') as image_file:
            response = self.client.post(reverse('blog_edit', kwargs={'blog_id': blog.id}), {'title': TITLE + EDITED_TITLE_SUFFIX, 'content': CONTENT + EDITED_CONTENT_SUFFIX, 'image': image_file}, follow=True)
            self.assertRedirects(response, f'/blog/{blog.id}/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
            self.assertTemplateUsed(response, 'blog_details.html')

            self.assertEqual(response.context['blog'].title, TITLE + EDITED_TITLE_SUFFIX)
            blog.refresh_from_db()
            self.assertEqual(blog.title, TITLE + EDITED_TITLE_SUFFIX)
            self.assertIn('comment_form', response.context.keys())
            self.assertEqual(blog.image, 'images/' + TEST_IMAGE)

            blog.image.delete()

    def test_blog_delete(self):
        ''' Удаление записи. Проверяем, что 
        GET анонима и неавтора редиректим на страницу поста
        GET автора ответ 200, верный шаблон, верный url
        POST автора ответ 200, верный шаблон, верный url
        POST блог отсутствует в БД, то есть удален
        '''

        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        for _ in range(2):
            response = self.client.get(reverse('blog_delete', kwargs={'blog_id': blog.id}), follow=True)
            self.assertRedirects(response, f'/blog/{blog.id}/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
            self.assertTemplateUsed(response, 'blog_details.html')

            self.assertTrue(Blog.objects.filter(title=TITLE).exists())

            self.client.login(username=USERNAME2, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)   
        
        self.client.logout()

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('blog_delete', kwargs={'blog_id': blog.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/delete/')
        self.assertTemplateUsed(response, 'form.html')
        self.assertTrue(Blog.objects.filter(title=TITLE).exists())

        response = self.client.post(reverse('blog_delete', kwargs={'blog_id': blog.id}), follow=True)
        self.assertRedirects(response, '/blogs/', status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK)
        self.assertTemplateUsed(response, 'blogs_list.html')

        self.assertFalse(Blog.objects.filter(title=TITLE).exists())

    def test_comment_create(self):
        ''' Создание комментария. Проверяем, что 
        0) GET/POST анонима редиректим на логин
        1) GET редиректим на главную
        2) POST ответ 200 после редиректа
        3) POST рендерится верный шаблон
        4) POST определяется верный url
        5) POST данные в контексте верны
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        response = self.client.get(reverse('comment_create', kwargs={'blog_id': blog.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')

        response = self.client.post(reverse('comment_create', kwargs={'blog_id': blog.id}), {'text': COMMENT_TEXT}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('comment_create', kwargs={'blog_id': blog.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('index.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/')

        response = self.client.post(reverse('comment_create', kwargs={'blog_id': blog.id}), {'text': COMMENT_TEXT}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('blog_details.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/')
        self.assertEqual(response.context['comments'][0].text, COMMENT_TEXT)

    def test_comment_delete(self):
        ''' Удаление записи. Проверяем, что 
        1) GET анонима и неавтора отправляем на страницу поста
        2) GET автора ответ 200
        3) GET автора рендерится верный шаблон 
        4) GET автора определяется верный url 
        5) GET комментарий отсутствует в БД, то есть удален
        '''
        blog = Blog(title=TITLE, content=CONTENT, author=self.user1)
        blog.save()

        comment = Comment(to_blog=blog, text=COMMENT_TEXT, author=self.user1)
        comment.save()

        for _ in range(2):
            response = self.client.get(reverse('comment_delete', kwargs={'blog_id': blog.id, 'comment_id': comment.id}), follow=True)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('blog_details.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/')
            self.assertTrue(Comment.objects.filter(text=COMMENT_TEXT).exists())

            self.client.login(username=USERNAME2, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)   
        
        self.client.logout()

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.post(reverse('comment_delete', kwargs={'blog_id': blog.id, 'comment_id': comment.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('blog_details.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], f'/blog/{blog.id}/')
        self.assertFalse(Comment.objects.filter(text=COMMENT_TEXT).exists())

    def test_bloggers_list(self):
        ''' Список блоггеров. Проверяем, что 
        1) возвращается верный статус страницы
        2) используется верный шаблон страницы 
        3) определяется верный url 
        4) в контексте есть нужная переменная 
        Сначала от имени анонима, потом от имени залогиненого юзера
        '''
        self.assertFalse(get_user(self.client).is_authenticated)

        for _ in range(2):
            response = self.client.get(reverse('bloggers_list'))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('bloggers_list.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], '/bloggers/')
            self.assertIn('bloggers', response.context.keys())

            self.client.login(username=USERNAME1, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)

    def test_bloggers_page(self):
        ''' Страница блоггера. Проверяем, что 
        1) возвращается верный статус страницы
        2) используется верный шаблон страницы 
        3) определяется верный url 
        4) в контексте есть нужные переменные
        Сначала от имени анонима, потом от имени залогиненого юзера
        '''
        blogger = User.objects.get(username=USERNAME1)

        self.assertFalse(get_user(self.client).is_authenticated)

        for _ in range(2):
            response = self.client.get(reverse('blogger_page', kwargs={'author_id': blogger.id}))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('blogger.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], f'/blogger/{blogger.id}/')
            self.assertIn('blogger', response.context.keys())
            self.assertIn('blogs', response.context.keys())
            self.assertIn('bio', response.context.keys())

            self.client.login(username=USERNAME2, password=PASSWORD)
            self.assertTrue(get_user(self.client).is_authenticated)

    def test_blogger_profile(self):
        ''' Редактирование профиля блоггера. Проверяем, что 
        1) GET/POST анонима отправляем на главную + проверяем, что ничего не изменилось
        2) GET ответ 200
        3) GET рендерится верный шаблон 
        4) GET определяется верный url 
        5) GET в контексте есть форма для редактирования био
        6) POST ответ 200 после редиректа
        7) POST рендерится верный шаблон
        8) POST определяется верный url
        10) данные в БД верны после апдейта, в том числе есть ссылка на аватар
        '''      
        self.assertFalse(get_user(self.client).is_authenticated)   

        response = self.client.get(reverse('blogger_profile'), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(response.request['QUERY_STRING'], 'next=%2Fblogger%2Fprofile%2F')

        response = self.client.post(reverse('blogger_profile'), {'bio': BIO_TO_TEST}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/accounts/login/')
        self.assertEqual(response.request['QUERY_STRING'], 'next=%2Fblogger%2Fprofile%2F')

        user = User.objects.get(username=USERNAME1)

        self.client.login(username=USERNAME1, password=PASSWORD)
        self.assertTrue(get_user(self.client).is_authenticated)

        response = self.client.get(reverse('blogger_profile'), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/blogger/profile/')
        self.assertIn('form', response.context.keys())
        
        with open('media/' + TEST_AVATAR, 'rb') as image_file:
            response = self.client.post(reverse('blogger_profile'), {'bio': BIO_TO_TEST, 'avatar': image_file}, follow=True)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn('index.html', [t.name for t in response.templates])
            self.assertEqual(response.request['PATH_INFO'], '/')
            user.refresh_from_db()
            self.assertEqual(user.blogger.bio, BIO_TO_TEST)
            self.assertEqual(user.blogger.avatar, 'avatars/' + TEST_AVATAR)

            blogger = user.blogger
            blogger.avatar.delete()

    def test_contacts(self):
        ''' Форма контакта. Проверяем, что 
        1) GET ответ 200
        2) GET рендерится верный шаблон 
        3) GET определяется верный url 
        4) GET в контексте есть форма
        5) POST ответ 200 после редиректа
        6) POST рендерится верный шаблон
        7) POST определяется верный url
        8) Письмо фактически отправлено
        '''
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/contacts/')
        self.assertIn('form', response.context.keys())

        response = self.client.post(reverse('contacts'), {'message': 'blabla'}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('index.html', [t.name for t in response.templates])
        self.assertEqual(response.request['PATH_INFO'], '/')

