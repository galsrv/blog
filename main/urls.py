from django.urls import path

from .cb_views import BlogCreateView, BlogDeleteView, BlogDetailView, BlogUpdateView, BloggerDetailView, BloggerProfileView, BloggersList, BlogsList, CommentCreateView, CommentDeleteView, IndexView


urlpatterns = [
    path('blogs/', BlogsList.as_view(), name='blogs_list'),
    path('blog/<int:blog_id>/', BlogDetailView.as_view(), name='blog_details'),
    path('blog/create/', BlogCreateView.as_view(), name='blog_create'),
    path('blog/<int:blog_id>/edit/', BlogUpdateView.as_view(), name='blog_edit'),
    path('blog/<int:blog_id>/delete/', BlogDeleteView.as_view(), name='blog_delete'),
    path('blog/<int:blog_id>/comment/create/', CommentCreateView.as_view(), name='comment_create'),
    path('blog/<int:blog_id>/comment/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('bloggers/', BloggersList.as_view(), name='bloggers_list'),
    path('blogger/profile/', BloggerProfileView.as_view(), name='blogger_profile'),
    path('blogger/<int:author_id>/', BloggerDetailView.as_view(), name='blogger_page'),
    path('', IndexView.as_view(), name='index'),
] 

