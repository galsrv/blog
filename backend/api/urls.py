from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from .cbviews import BlogCRUD, CommentDelete, BloggersListRetrieve


router = SimpleRouter(use_regex_path=False)

router.register('blogs', BlogCRUD)

router.register('bloggers', BloggersListRetrieve, basename='api-bloggers')

urlpatterns = [
    re_path(r'^v1/auth/', include('djoser.urls')),
    re_path(r'^v1/auth/', include('djoser.urls.authtoken')),
    path('v1/blogs/<int:id>/comment/<int:comment_id>/', CommentDelete.as_view(), name='api-comment-delete'),
    # path('v1/bloggers/<int:id>/', BloggersListRetrieve.as_view({'get': 'retrieve'})),
    # path('v1/bloggers/', BloggersListRetrieve.as_view({'get': 'list'})),
    path('v1/', include(router.urls)),
    # path('v1/blogs/', BlogCRUD.as_view({'get': 'list'})),
    # path('v1/blogs/', BlogsListCreate.as_view()),
    # path('v1/blogs/<int:id>/', BlogRUD.as_view()),
]