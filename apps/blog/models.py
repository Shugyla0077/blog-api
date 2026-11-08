from django.conf import settings
from django.db import models

from apps.blog.constants import (
    MAX_CATEGORY_NAME_LENGTH,
    MAX_POST_STATUS_LENGTH,
    MAX_POST_TITLE_LENGTH,
    MAX_TAG_NAME_LENGTH,
)


class Category(models.Model):
    name = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_NAME_LENGTH, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    title = models.CharField(max_length=MAX_POST_TITLE_LENGTH)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
    )
    status = models.CharField(
        max_length=MAX_POST_STATUS_LENGTH,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Comment by {self.author} on {self.post}'