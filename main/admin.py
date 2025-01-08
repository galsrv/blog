from django.contrib import admin

from .models import Blog, Blogger, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    readonly_fields = ['created', ]
    extra = 0

class BlogAdmin(admin.ModelAdmin):
    inlines = [CommentInline, ]


admin.site.register(Blogger)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)
