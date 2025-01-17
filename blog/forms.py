from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField, Form


# class BlogUserCreationForm(UserCreationForm):
#     bio = CharField(max_length=200, label='Enter some of your bio facts')


class ContactForm(Form):
    message = CharField(max_length=1000, label='Enter your message')