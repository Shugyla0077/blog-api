import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpRequest

from apps.blog.constants import TOP_AUTHORS_COUNT
from apps.blog.models import Category, Comment, Post
from settings.conf import ENV_ID

User = get_user_model()


def environment_callback(request: HttpRequest) -> list[str]:
    return ['Production', 'danger'] if ENV_ID == 'prod' else ['Local', 'warning']


def drafts_badge(request: HttpRequest) -> int:
    return Post.objects.filter(status=Post.Status.DRAFT).count()


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    users_cnt = User.objects.count()
    pub_cnt = Post.objects.filter(status=Post.Status.PUBLISHED).count()
    draft_cnt = Post.objects.filter(status=Post.Status.DRAFT).count()
    total_posts = pub_cnt + draft_cnt
    comments_cnt = Comment.objects.count()

    pub_pct = round(pub_cnt * 100 / total_posts) if total_posts else 0
    draft_pct = 100 - pub_pct if total_posts else 0

    cats = Category.objects.annotate(cnt=Count('posts')).order_by('-cnt')
    chart_data = json.dumps({
        'labels': [c.name for c in cats],
        'datasets': [{'label': 'Posts', 'data': [c.cnt for c in cats], 'backgroundColor': '#10b981'}],
    })

    top_authors = User.objects.annotate(cnt=Count('posts')).order_by('-cnt')[:TOP_AUTHORS_COUNT]

    context.update({
        'cards': [
            {'title': 'Users', 'metric': users_cnt},
            {'title': 'Published Posts', 'metric': pub_cnt},
            {'title': 'Drafts', 'metric': draft_cnt},
            {'title': 'Comments', 'metric': comments_cnt},
        ],
        'chart_data': chart_data,
        'top_authors': {
            'headers': ['Email', 'Name', 'Posts'],
            'rows': [[u.email, f'{u.first_name} {u.last_name}', u.cnt] for u in top_authors],
        },
        'pub_pct': pub_pct,
        'draft_pct': draft_pct,
    })
    return context