import os

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from dotenv import load_dotenv

from .forms import ContactForm
from main.models import Blogger

load_dotenv()

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'form.html'
    extra_context = {'title': 'Signup page'}
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        self.object = form.save()
        Blogger.objects.create(user=self.object)
        return super().form_valid(form)

class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'form.html'
    extra_context = {'title': 'Login page'}


class LogoutUser(LogoutView):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        # Не самый элегантный, но вынужденный способ разлогинитсья по GET
        logout(request)
        return redirect('index')


class ContactsFormView(FormView):
    template_name = 'form.html'
    form_class = ContactForm
    success_url = reverse_lazy('index')
    extra_context = {'title': 'Contact form'}

    def form_valid(self, form):
        message = form.cleaned_data['message']

        send_mail(
            subject='Message from contact form',
            message=message,
            from_email=os.getenv('FROM_EMAIL'),
            recipient_list=[os.getenv('FROM_EMAIL'), ],
            fail_silently=True,
        )

        return super().form_valid(form)
