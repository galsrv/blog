from django.db.models import DateTimeField, CASCADE, CharField, ForeignKey, Model, OneToOneField, TextField

from django.contrib.auth.models import User
from django.urls import reverse


class Blogger(Model):
    user = OneToOneField(User, unique=True, on_delete=CASCADE, related_name='blogger')
    bio = TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f'Блогер: {self.user.username}'

    def get_absolute_url(self):
        return reverse('blogger_page', kwargs={'author_id': self.user.pk})


class Blog(Model):
    title = CharField(max_length=50)
    content = TextField(max_length=2000)
    created = DateTimeField(auto_now_add=True)
    author = ForeignKey(to=User, on_delete=CASCADE, related_name='blogs')

    class Meta:
        ordering = ['-created', ]

    def __str__(self):
        return f'Запись: {self.title[:10]}'

    def get_absolute_url(self):
        return reverse('blog_details', kwargs={'blog_id': self.pk})

    @property
    def nr_comments(self):
        return self.comments.count()


class Comment(Model):
    to_blog = ForeignKey(to=Blog, on_delete=CASCADE, related_name='comments')
    text = TextField(max_length=1000)
    author = ForeignKey(to=User, on_delete=CASCADE, related_name='comments_by_author')
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created', ]

    def __str__(self):
        return f'Комментарий: {self.text[:10]}'