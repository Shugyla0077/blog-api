from typing import Any

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.sections import TableSection

from django.contrib import admin
from django.db import models
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from apps.blog.constants import COMMENTS_PER_PAGE, SHORT_BODY_LEN
from apps.blog.models import Category, Comment, Post, Tag


class CategoryPostsSection(TableSection):
    verbose_name = 'Posts'
    related_name = 'posts'
    fields = ['title', 'status', 'created_at']


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'posts_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Category]:
        return super().get_queryset(request).annotate(p_cnt=Count('posts')).prefetch_related('posts')

    @display(description='Posts', ordering='p_cnt')
    def posts_count(self, obj: Category) -> int:
        return getattr(obj, 'p_cnt', 0)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'posts_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[Tag]:
        return super().get_queryset(request).annotate(p_cnt=Count('posts'))

    @display(description='Posts', ordering='p_cnt')
    def posts_count(self, obj: Tag) -> int:
        return getattr(obj, 'p_cnt', 0)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('post', 'author', 'short_body', 'created_at')
    list_select_related = ('post', 'author')
    list_filter_submit = True
    list_filter = (
        ('post', AutocompleteSelectFilter),
        ('author', AutocompleteSelectFilter),
        ('created_at', RangeDateTimeFilter),
    )
    search_fields = ('body', 'author__email', 'post__title')
    autocomplete_fields = ('post', 'author')

    @display(description='Body')
    def short_body(self, obj: Comment) -> str:
        return obj.body[:SHORT_BODY_LEN]


class PostCommentsSection(TableSection):
    verbose_name = 'Comments'
    related_name = 'comments'
    fields = ['author', 'body', 'created_at']


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    tab = True
    per_page = COMMENTS_PER_PAGE
    autocomplete_fields = ('author',)
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('post_header', 'status_label', 'category', 'tags_dropdown', 'comments_count', 'created_at')
    list_select_related = ('author', 'category')
    list_filter_submit = True
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('category', RelatedDropdownFilter),
        ('tags', MultipleRelatedDropdownFilter),
        ('author', AutocompleteSelectFilter),
        ('created_at', RangeDateTimeFilter),
    )
    search_fields = ('title', 'body', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('author', 'category', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    warn_unsaved_form = True
    inlines = [CommentInline]
    list_sections = [PostCommentsSection]
    formfield_overrides = {models.TextField: {'widget': WysiwygWidget}}

    fieldsets = (
        ('Content', {'classes': ['tab'], 'fields': ('title', 'slug', 'body')}),
        ('Classification', {'classes': ['tab'], 'fields': ('category', 'tags', 'status')}),
        ('Meta', {'classes': ['tab'], 'fields': ('author', 'created_at', 'updated_at')}),
    )

    actions = ['publish_selected', 'move_to_drafts']
    actions_row = ['toggle_publish']
    actions_list = ['publish_all_drafts']
    actions_detail = ['open_comments']
    actions_submit_line = ['save_and_publish']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related('tags', 'comments__author')
            .annotate(c_cnt=Count('comments', distinct=True))
        )

    @display(description='Post', header=True)
    def post_header(self, obj: Post) -> list[str]:
        return [obj.title, obj.author.email]

    @display(description='Status', label={'published': 'success', 'draft': 'warning'})
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description='Tags', dropdown=True)
    def tags_dropdown(self, obj: Post) -> dict[str, Any]:
        tags = obj.tags.all()
        return {'title': f'{len(tags)} tags', 'items': [{'title': t.name} for t in tags]}

    @display(description='Comments', ordering='c_cnt')
    def comments_count(self, obj: Post) -> int:
        return getattr(obj, 'c_cnt', 0)

    @action(description='Publish selected')
    def publish_selected(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        queryset.update(status=Post.Status.PUBLISHED)

    @action(description='Move to drafts')
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet[Post]) -> None:
        queryset.update(status=Post.Status.DRAFT)

    @action(description='Publish / unpublish', url_path='toggle-publish')
    def toggle_publish(self, request: HttpRequest, object_id: int) -> HttpResponseRedirect:
        post = Post.objects.get(pk=object_id)
        post.status = Post.Status.DRAFT if post.status == Post.Status.PUBLISHED else Post.Status.PUBLISHED
        post.save(update_fields=['status'])
        return redirect(reverse('admin:blog_post_changelist'))

    @action(description='Publish all drafts', url_path='publish-all')
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponseRedirect:
        Post.objects.filter(status=Post.Status.DRAFT).update(status=Post.Status.PUBLISHED)
        return redirect(reverse('admin:blog_post_changelist'))

    @action(description="Open this post's comments", url_path='open-comments')
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponseRedirect:
        return redirect(f"{reverse('admin:blog_comment_changelist')}?post={object_id}")

    @action(description='Save & publish')
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save(update_fields=['status'])