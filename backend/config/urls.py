from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .settings import DEBUG, MEDIA_ROOT, MEDIA_URL
from .cb_views import ContactsFormView, LoginUser, LogoutUser, SignupView


accounts_patterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login/', LoginUser.as_view(), name='mylogin'),
    path('logout/', LogoutUser.as_view(), name='mylogout'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts_patterns)),
    path('contacts/', ContactsFormView.as_view(), name='contacts'),
    path('api/', include('api.urls')),
    path('', include('main.urls')),
] + debug_toolbar_urls()

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)


schema_view = get_schema_view(
   openapi.Info(
      title="Blog API",
      default_version='v1',
      description="API description for Blog Project",
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]