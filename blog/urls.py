from django.contrib import admin

from django.urls import include, path

from blog.cb_views import ContactsFormView, LoginUser, LogoutUser, SignupView


accounts_patterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts_patterns)),
    path('contacts/', ContactsFormView.as_view(), name='contacts'),
    path('', include('main.urls')),
]

