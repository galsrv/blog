from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic.base import TemplateView

from main.constants import BLOGS_PER_PAGE
from main.forms import BloggerForm, CommentForm
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
    queryset = User.objects.annotate(nr_blogs=Count('blogs'))
    ordering = ['-nr_blogs', ]
    context_object_name = 'bloggers'


class BloggerDetailView(DetailView):
    http_method_names = ['get', 'head']
    template_name = 'blogger.html'
    model = User
    context_object_name = 'blogger'
    pk_url_kwarg = 'author_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(author=self.object.id).order_by('-created')
        context['bio'] = ''
        try:
            blogger_entry = Blogger.objects.get(user=self.object.id)
            context['bio'] = blogger_entry.bio
        except Blogger.DoesNotExist:
            context['bio'] = 'The user didn\'t provide any bio' 

        return context


class BloggerProfileView(LoginRequiredMixin, FormView):
    form_class = BloggerForm
    template_name = 'form.html'
    extra_context = {'title': 'Edit your bio page'}

    def get_blogger(self, user):
        blogger, _ = Blogger.objects.get_or_create(user=user, defaults={'bio': ''})
        return blogger

    def get_initial(self):
        blogger = self.get_blogger(self.request.user)
        return {'bio': blogger.bio}

    def form_valid(self, form: BloggerForm):
        blogger = self.get_blogger(self.request.user) 
        blogger.bio = form.cleaned_data['bio']
        blogger.save()
        return redirect('index')


class BlogsList(ListView):
    http_method_names = ['get', 'head']
    template_name = 'blogs_list.html'
    model = Blog
    ordering = ['-created', ]
    paginate_by = BLOGS_PER_PAGE


class BlogDetailView(DetailView):
    http_method_names = ['get', 'head']
    model = Blog
    pk_url_kwarg = 'blog_id'
    context_object_name = 'blog'
    template_name = 'blog_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['comments'] = Comment.objects.filter(to_blog=self.object).annotate(
            comment_author_flag=Case(
                When(author=self.request.user if self.request.user.is_authenticated else None, then=True),
                default=False))
        context['author_flag'] = self.object.author == self.request.user
        context['comment_form'] = CommentForm()

        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content']
    template_name = 'form.html'
    extra_context = {'title': 'Create new blog entry'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    model = Blog
    fields = ['title', 'content']
    template_name = 'form.html'
    extra_context = {'title': 'Update the blog entry'}
    pk_url_kwarg = 'blog_id'

    def dispatch(self, request, *args, **kwargs):
        # Такой способ проверки на автора объекта казался мне фиговым
        # Пока я не увидел, что в материалах Яндекс Практикума рекомендуется делать именно так
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
