from django.urls import path

from .fb_views import blog_create, blog_delete, blog_details, blog_edit, blogger_page, bloggers_list, blogs_list, comment_delete, index


urlpatterns = [
    path('blogs/', blogs_list, name='blogs_list'),
    path('blogs/<int:blog_id>/', blog_details, name='blog_details'),
    path('blogs/create/', blog_create, name='blog_create'),
    path('blogs/edit/<int:blog_id>/', blog_edit, name='blog_edit'),
    path('blogs/delete/<int:blog_id>/', blog_delete, name='blog_delete'),
    path('blogs/comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),
    path('bloggers/', bloggers_list, name='bloggers_list'),
    path('bloggers/<int:author_id>/', blogger_page, name='blogger_page'),
    path('', index, name='index'),
] 