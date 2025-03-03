from http import HTTPMethod

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import DestroyAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthenticatedOrReadOnlyPlusOwnerControl
from .serializers import BlogSerializer, BlogSimpleSerializer, CommentSerializer, BloggerSerializer, BloggerProfileSerializer
from main.models import Blog, Blogger, Comment

User = get_user_model()


class BlogCRUD(ModelViewSet):
    ''' CRUD операции с записями блога '''
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyPlusOwnerControl, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=[HTTPMethod.POST, ], detail=True)
    def comment(self, request, pk):
        ''' Создаем новый комментарий к данному блогу '''
        blog = get_object_or_404(Blog, id=pk)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(to_blog=blog, author=request.user)

        blog_serializer = BlogSerializer(blog)
        return Response(blog_serializer.data, status=status.HTTP_201_CREATED)


class CommentDelete(DestroyAPIView):
    ''' Представление для удаления комментария '''
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyPlusOwnerControl, ]
    lookup_url_kwarg = 'comment_id'


class BloggersListRetrieve(ModelViewSet):
    ''' Представление для получения отдельного блоггера либо списка блоггеров '''
    http_method_names = ['get', 'patch']
    queryset = User.objects.all()
    serializer_class = BloggerSerializer
    lookup_field = 'id'
    pagination_class = None

    def partial_update(self, request, *args, **kwargs):
        # Вынужденное решение. Чтобы не выносить profile в отдельный класс. Нужно, чтобы вьюсет разрешал patch-запросы
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch', ], detail=True, permission_classes = [IsAuthenticatedOrReadOnlyPlusOwnerControl, ])
    def profile(self, request: Request, id):
        # Изменяем поля bio & avatar таблицы Blogger
        # Меняем данные таблицы Blogger, но выводим обогащенную запись из User
        user = get_object_or_404(User, id=id)
        # Проверяем, что запрос направил сам пользователь
        self.check_object_permissions(request, user)
        user_serializer = BloggerSerializer(user)

        blogger = user.blogger
        blogger_serializer = BloggerProfileSerializer(data=request.data, instance=blogger, partial=True)

        if blogger_serializer.is_valid():
            blogger_serializer.save()
        else:
            return Response(blogger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(user_serializer.data)


class BloggerProfileUpdate(UpdateAPIView):
    ''' Представление для обновления профиля блоггера '''
    http_method_names = ['patch', ]
    queryset = Blog.objects.all()
    serializer_class = BloggerProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyPlusOwnerControl, ]

    def get_object(self):
        # Подмена объекта. Обращаемся по айди User, а менять будем Blogger
        blog = super().get_object()
        return blog.blogger


class BlogsListCreate(ListCreateAPIView):
    ''' Список блогов и создание новых записей '''
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class BlogRUD(RetrieveUpdateDestroyAPIView):
    ''' Получение, изменение и удаление отдельной записи блога'''
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer   
    lookup_field = 'id'


class BlogsListCreateAPIView(APIView):
    ''' Эксперимент с обычным сериалайзером и APIView '''
    http_method_names = ['get', 'post']

    def get(self, request: Request):
        blogs = Blog.objects.all()
        serializer = BlogSimpleSerializer(blogs, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = BlogSimpleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BlogDetailAPIView(APIView):
    ''' Эксперимент с обычным сериалайзером и APIView '''
    http_method_names = ['get', 'put', 'patch', 'delete']

    def blog_entry_retrieve(self, id: int) -> Blog:
        return get_object_or_404(Blog, id=id)

    def get(self, request: Request, id):
        blog = self.blog_entry_retrieve(id)
        serializer = BlogSimpleSerializer(blog)
        return Response(serializer.data)

    def put(self, request: Request, id):
        blog = self.blog_entry_retrieve(id)
        serializer = BlogSimpleSerializer(data=request.data, instance=blog)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request: Request, id):
        blog = self.blog_entry_retrieve(id)
        serializer = BlogSimpleSerializer(data=request.data, instance=blog, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, id):
        blog = self.blog_entry_retrieve(id)
        blog.delete()
        return Response({'status': 'object deleted'}, status=status.HTTP_204_NO_CONTENT)
