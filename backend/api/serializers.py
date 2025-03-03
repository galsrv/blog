from django.contrib.auth import get_user_model
from rest_framework import serializers

from main.models import Blog, Blogger, Comment

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created', 'author']


class BlogSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'created', 'author', 'image', 'comments']


class BlogShortSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    comments_nr = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'created', 'url', 'comments_nr']

    def get_url(self, obj: Blog):
        return obj.get_absolute_url()

    def get_comments_nr(self, obj: Blog):
        return obj.comments.count()


class BloggerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blogger
        fields = ['bio', 'avatar']


class BloggerSerializer(serializers.ModelSerializer):
    blogs = BlogShortSerializer(read_only=True, many=True)
    blogger = BloggerProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'blogger', 'blogs']


class BlogSimpleSerializer(serializers.Serializer):
    ''' Эксперимент с обычным сериалайзером '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=50)
    content = serializers.CharField(max_length=20000)
    created = serializers.DateTimeField(read_only=True)
    author_id = serializers.IntegerField()
    image = serializers.ImageField(default='default_image.jpg')

    def create(self, validated_data):
        return Blog.objects.create(**validated_data)

    def update(self, instance: Blog, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.author_id = id=validated_data.get('author_id', instance.author_id)
        instance.save()

        return instance
