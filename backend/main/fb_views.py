from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Case, Count, When
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from .constants import BLOGS_PER_PAGE
from .forms import BlogForm, CommentForm
from .models import Blog, Comment

User = get_user_model()

def index(request, *args, **kwargs):
    return render(request, 'index.html')

def blogs_list(request: HttpRequest, *args, **kwargs):
    blogs = Blog.objects.order_by('-created')
    paginator = Paginator(blogs, BLOGS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request, 'blogs_list.html', context={'page_obj': page_obj})

def blog_details(request: HttpRequest, blog_id: int, *args, **kwargs):
    blog = get_object_or_404(Blog, id=blog_id)
    
    if request.method == 'POST' and request.user.is_authenticated:
        new_comment = Comment(to_blog=blog, author=request.user)
        comment_form = CommentForm(request.POST, instance=new_comment)

        if comment_form.is_valid():
            comment_form.save()

    comments = Comment.objects.filter(to_blog=blog).annotate(
        comment_author_flag=Case(
            When(author=request.user if request.user.is_authenticated else None, then=True),
            default=False))
    author_flag = blog.author == request.user 

    comment_form = CommentForm()

    return render(request, 'blog_details.html', context={
        'blog': blog,
        'comments': comments,
        'author_flag': author_flag,
        'comment_form': comment_form})

def blog_create(request: HttpRequest, *args, **kwargs):
    user = request.user

    if not user.is_authenticated or not hasattr(user, 'blogger'):
        return redirect('index')
    
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = Blog()
            blog.title = form.cleaned_data['title']
            blog.content = form.cleaned_data['content']
            blog.author = user
            blog.save()
            return redirect('blog_details', blog_id=blog.id)

    form = BlogForm()

    return render(request, 'blog_create.html', {'form': form})

def blog_edit(request: HttpRequest, blog_id: int, *args, **kwargs):
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)

    if not user.is_authenticated or user != blog.author:
        return redirect('blog_details', blog_id=blog.id)

    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog.title = form.cleaned_data['title']
            blog.content = form.cleaned_data['content']
            blog.save()
            return redirect('blog_details', blog_id=blog.id)
    else:
        form = BlogForm()
        form.data['title'] = blog.title
        form.data['content'] = blog.content
        form.is_bound = True

    return render(request, 'blog_edit.html', {'form': form, 'blog': blog})

def blog_delete(request: HttpRequest, blog_id: int, *args, **kwargs):
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)

    if user.is_authenticated and user == blog.author:
        blog.delete()
        return redirect('blogs_list')
    
    return redirect('blog_details', blog_id=blog.id)

def bloggers_list(request: HttpRequest, *args, **kwargs):
    if request.method == 'GET':
        bloggers = User.objects.filter(blogger__isnull=False).annotate(nr_blogs=Count('blogs'))
        return render(request, 'bloggers_list.html', context={'bloggers': bloggers})
    return redirect(to='bloggers_list')

def blogger_page(request: HttpRequest, author_id: int, *args, **kwargs):
    if request.method == 'GET':
        blogger = get_object_or_404(User, id=author_id, blogger__isnull=False)
        blogs = Blog.objects.filter(author=blogger).order_by('-created')
        return render(request, 'blogger.html', context={'blogger': blogger, 'blogs': blogs})
    return redirect(to='blogger_page', author_id=author_id)

def comment_delete(request: HttpRequest, comment_id: int, *args, **kwargs):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if request.user.is_authenticated and user == comment.author:
        comment.delete()

    return redirect('blog_details', blog_id=comment.to_blog.id)



