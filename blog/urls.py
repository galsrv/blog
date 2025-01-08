from django.contrib import admin
from django.contrib.auth.views import LoginView

from django.urls import include, path, reverse_lazy

from blog.views import contacts, logout_view, signup


accounts_patterns = [
    path('signup', signup, name='signup'),
    path('login/', LoginView.as_view(
        template_name='form.html',
        next_page=reverse_lazy('index'),
        extra_context={'title': 'Login page'}),
        name='login'),
    path('logout/', logout_view, name='logout'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts_patterns)),
    path('contacts/', contacts, name='contacts'),
    path('', include('main.urls')),
]

