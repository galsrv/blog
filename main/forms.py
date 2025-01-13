from django.forms import CharField, Form, ModelForm, Textarea

from .models import Comment

class BlogForm(Form):
    title = CharField(max_length=50)
    content = CharField(max_length=2000, widget=Textarea)


class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ['text', ]


class BloggerForm(Form):
    bio = CharField(max_length=2000, required=False)