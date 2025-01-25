from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, F, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, View, UpdateView
from django.views.generic.base import TemplateView

from main.constants import BLOGS_PER_PAGE
from main.forms import BioForm, BloggerForm, CommentForm
from main.models import Blog, Blogger, Comment


User = get_user_model()


class IndexView(TemplateView):
    http_method_names = ['get', 'head']
    template_name = 'index.html'

    def http_method_not_allowed(self, request, *args, **kwargs):
        return render(request, '405.html')


class BloggersList(ListView):
    http_method_names = ['get', 'head']
    template_name = 'bloggers_list.html'
    model = User
    context_object_name = 'bloggers'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            nr_blogs=Count('blogs'),
            avatar=F('blogger__avatar')).order_by('-nr_blogs')
        return queryset

    def get_template_names(self):
        # В случае HTMX те же данные нужно отправить в другой шаблон
        if self.request.path == '/bloggers/htmx/':
            return 'includes/htmx_bloggers_list.html'
        return super().get_template_names()


class BloggerDetailView(DetailView):
    http_method_names = ['get', 'head']
    template_name = 'blogger.html'
    queryset = User.objects.annotate(avatar=F('blogger__avatar'))
    context_object_name = 'blogger'
    pk_url_kwarg = 'author_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(author=self.object.id).annotate(nr_comments=Count('comments')).order_by('-created')
        context['bio'] = ''
        context['author_id'] = self.object.id
        try:
            blogger_entry = Blogger.objects.get(user=self.object.id)
            context['bio'] = blogger_entry.bio
        except Blogger.DoesNotExist:
            context['bio'] = 'The user didn\'t provide any bio' 
        context['update_bio_flag'] = self.request.user.id == self.object.id

        return context


class BioUpdateView(View):

    def get(self, request, *args, **kwargs):
        author_id = self.kwargs['author_id']
        blogger = get_object_or_404(Blogger, user=author_id)
        form = BioForm(initial={'bio': blogger.bio})
        return render(request, 'includes/htmx_bio_form.html', context={'form': form, 'author_id': author_id})       

    def post(self, request, *args, **kwargs):
        author_id = self.kwargs['author_id']
        context = {
            'update_bio_flag': request.user.id == author_id,
            'author_id': author_id,
            'bio': ''
        }
        form = BioForm(request.POST)
        if form.is_valid():
            blogger = get_object_or_404(Blogger, user=author_id)
            blogger.bio = form.cleaned_data['bio']
            if context['update_bio_flag']:
                blogger.save()
            context['bio'] = blogger.bio
        return render(request, 'includes/htmx_bio.html', context)        


class BloggerProfileView(LoginRequiredMixin, FormView):
    form_class = BloggerForm
    template_name = 'form.html'
    extra_context = {'title': 'Edit your bio page',}

    def get_blogger(self, user):
        blogger, _ = Blogger.objects.get_or_create(user=user)
        return blogger

    def get_initial(self):
        blogger = self.get_blogger(self.request.user)
        return {'bio': blogger.bio, 'avatar': blogger.avatar}

    def form_valid(self, form: BloggerForm):
        blogger = self.get_blogger(self.request.user) 
        blogger.bio = form.cleaned_data['bio']
        blogger.avatar = form.cleaned_data['avatar']
        blogger.save()
        return redirect('index')


class BlogsList(ListView):
    http_method_names = ['get', 'head']
    template_name = 'blogs_list.html'
    model = Blog
    ordering = ['-created', ]
    paginate_by = BLOGS_PER_PAGE

    def get_queryset(self):
        # "Retrieve everything at once if you know you will need it" (c)
        # Оптимизация числа запросов к БД
        queryset = super().get_queryset()
        from django.db.models import F
        queryset = queryset.annotate(
            nr_comments=Count('comments'),
            author_username=F('author__username'),
            author_iid=F('author__id'),)
        return queryset


class BlogDetailView(DetailView):
    http_method_names = ['get', 'head']
    model = Blog
    pk_url_kwarg = 'blog_id'
    context_object_name = 'blog'
    template_name = 'blog_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['comments'] = Comment.objects.filter(to_blog=self.object).annotate(
            author_username=F('author__username'),
            author_iid=F('author__id'),
            comment_author_flag=Case(
                When(author=self.request.user if self.request.user.is_authenticated else None, then=True),
                default=False))
        # Думал избавиться от лишнего запроса к БД, но DetailView записывает в контекст объект модели, а QuerySet
        # И мой любимый прием с annotate к объекту модели не прикрутишь ((
        context['author_flag'] = self.object.author == self.request.user
        context['comment_form'] = CommentForm()

        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'form.html'
    extra_context = {'title': 'Create new blog entry'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'form.html'
    extra_context = {'title': 'Update the blog entry'}
    pk_url_kwarg = 'blog_id'

    def dispatch(self, request, *args, **kwargs):
        # этот метод выполняется на старте, поэтому от LoginRequiredMixin уже никакого эффекта нет
        blog = self.get_object()
        if request.user != blog.author:
            return redirect(blog)

        return super().dispatch(request, *args, **kwargs)


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'form.html'
    pk_url_kwarg = 'blog_id'
    success_url = reverse_lazy('blogs_list')

    def dispatch(self, request, *args, **kwargs):
        blog = self.get_object()
        if request.user != blog.author:
            return redirect(blog)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['title'] = f'Please confirm the entry "{blog.title}" removal'
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    http_method_names = ['post', ]
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.to_blog = get_object_or_404(Blog, id=self.kwargs['blog_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog_details', kwargs=self.kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return redirect('index')


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'form.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.author:
            return redirect(comment.to_blog)

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        context['title'] = f'Please confirm the comment "{comment.text}" removal'
        return context

    def get_success_url(self):
        return reverse('blog_details', kwargs={'blog_id': self.kwargs['blog_id']})
