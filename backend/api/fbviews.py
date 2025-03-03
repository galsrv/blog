from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from main.models import Blog

User = get_user_model()

@api_view()
def blogs(request: Request):
    blogs = Blog.objects.all().values()
    return Response(blogs)

@api_view()
def blog_details(request: Request, id):
    # Все ручные способы сериализации инстанса модели - допольно специфичные
    # https://stackoverflow.com/questions/21925671/convert-django-model-object-to-dict-with-all-of-the-fields-intact
    blog = Blog.objects.filter(id=id).values()[0]
    return Response(blog)

@api_view(http_method_names=['POST'])
def blog_create(request: Request):
    blog_to_create = Blog.objects.create(
        title = request.data['title'],
        content = request.data['content'],
        author = User.objects.get(id=request.data['author'])
    )
    # см комментарий выше
    blog = Blog.objects.filter(id=blog_to_create.id).values()[0]
    return Response(blog, status=status.HTTP_201_CREATED)

@api_view(http_method_names=['DELETE'])
def blog_delete(request: Request, id):
    Blog.objects.get(id=id).delete()
    return Response({'status': 'object deleted'}, status=status.HTTP_204_NO_CONTENT)