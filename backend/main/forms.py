from django.forms import CharField, FileInput, Form, ImageField, ModelForm

from .models import Comment


class CommentForm(ModelForm):
    
    class Meta:
        model = Comment
        fields = ['text', ]


class BloggerForm(Form):
    bio = CharField(max_length=2000, required=False)
    avatar = ImageField(required=False, widget=FileInput)


class BioForm(Form):
    bio = CharField(max_length=2000, required=True)