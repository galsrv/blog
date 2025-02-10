from django.forms import CharField, Form


class ContactForm(Form):
    message = CharField(max_length=1000, label='Enter your message')