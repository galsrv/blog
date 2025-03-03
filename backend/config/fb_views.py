from django.contrib.auth import logout
from django.http import HttpRequest
from django.shortcuts import redirect, render

from config.forms import BlogUserCreationForm, ContactForm
from main.models import Blogger


def signup(request: HttpRequest, *args, **kwargs):
    
    if request.user.is_authenticated:
        return redirect('index')

    form = BlogUserCreationForm()

    if request.method == 'POST':
        form = BlogUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Blogger.objects.create(user=user, bio=form.cleaned_data['bio'])
            return redirect('mylogin')

    return render(request, 'form.html', context={'form': form, 'title': 'Signup page'})

def logout_view(request: HttpRequest, *args, **kwargs):
    logout(request)
    return redirect('index')


def contacts(request: HttpRequest, *args, **kwargs):
    form = ContactForm()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            # Add sending email
            return redirect('index')

    return render(request, 'form.html', context={'form': form, 'title': 'Contacts page'})

