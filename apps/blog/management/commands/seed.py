import random
import time
from typing import Any

from faker import Faker

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.text import slugify

from apps.blog.constants import (
    CATEGORIES,
    DEFAULT_COMMENTS,
    DEFAULT_POSTS,
    DEFAULT_USERS,
    SEED_PASSWORD,
    TAGS,
)
from apps.blog.models import Category, Comment, Post, Tag

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Fill the database with fake data.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--users', type=int, default=DEFAULT_USERS)
        parser.add_argument('--posts', type=int, default=DEFAULT_POSTS)
        parser.add_argument('--comments', type=int, default=DEFAULT_COMMENTS)
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args: Any, **options: Any) -> None:
        start = time.perf_counter()
        u_cnt: int = options['users']
        p_cnt: int = options['posts']
        c_cnt: int = options['comments']

        if min(u_cnt, p_cnt, c_cnt) < 0:
            raise CommandError('Counts cannot be negative.')

        if options['clear']:
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

       
        used_emails = set(User.objects.values_list('email', flat=True))
        password_hash = make_password(SEED_PASSWORD)
        new_users = []
        for i in range(u_cnt):
            first, last = fake.first_name(), fake.last_name()
            email = f'{first.lower()}.{last.lower()}.{i}@example.com'
            while email in used_emails:
                email = f'{first.lower()}.{random.randint(100, 9999)}@example.com'
            used_emails.add(email)
            new_users.append(
                User(
                    email=email,
                    first_name=first,
                    last_name=last,
                    password=password_hash,
                    is_active=random.random() > 0.1,
                    is_staff=random.random() < 0.1,
                )
            )
        User.objects.bulk_create(new_users)
        users = list(User.objects.all())
        if (p_cnt > 0 or c_cnt > 0) and not users:
            raise CommandError('No users available to create posts or comments.')

        
        existing_cats = set(Category.objects.values_list('name', flat=True))
        cats_to_create = [
            Category(name=n, slug=slugify(n)) for n in CATEGORIES if n not in existing_cats
        ]
        Category.objects.bulk_create(cats_to_create)
        categories = list(Category.objects.all())

        existing_tags = set(Tag.objects.values_list('name', flat=True))
        tags_to_create = [
            Tag(name=n, slug=slugify(n)) for n in TAGS if n not in existing_tags
        ]
        Tag.objects.bulk_create(tags_to_create)
        tags = list(Tag.objects.all())

        
        used_slugs = set(Post.objects.values_list('slug', flat=True))
        new_posts = []
        for _ in range(p_cnt):
            title = fake.sentence(nb_words=5).rstrip('.')
            base_slug = slugify(title) or 'post'
            slug, n = base_slug, 2
            while slug in used_slugs:
                slug = f'{base_slug}-{n}'
                n += 1
            used_slugs.add(slug)

            new_posts.append(
                Post(
                    author=random.choice(users),
                    title=title,
                    slug=slug,
                    body='\n\n'.join(fake.paragraphs(nb=3)),
                    category=None if random.random() < 0.1 else random.choice(categories),
                    status=Post.Status.PUBLISHED if random.random() < 0.7 else Post.Status.DRAFT,
                )
            )
        created_posts = Post.objects.bulk_create(new_posts)
        for post in created_posts:
            post.tags.set(random.sample(tags, k=random.randint(0, 5)))

        
        pub_posts = list(Post.objects.filter(status=Post.Status.PUBLISHED))
        if c_cnt > 0 and not pub_posts:
            raise CommandError('No published posts available for comments.')

        new_comments = [
            Comment(
                post=random.choice(pub_posts),
                author=random.choice(users),
                body=fake.paragraph(nb_sentences=2),
            )
            for _ in range(c_cnt)
        ]
        Comment.objects.bulk_create(new_comments)

        self.stdout.write(self.style.SUCCESS(f'Users: {len(new_users)} created'))
        self.stdout.write(self.style.SUCCESS(f'Categories: {len(cats_to_create)} created'))
        self.stdout.write(self.style.SUCCESS(f'Tags: {len(tags_to_create)} created'))
        self.stdout.write(self.style.SUCCESS(f'Posts: {len(created_posts)} created'))
        self.stdout.write(self.style.SUCCESS(f'Comments: {len(new_comments)} created'))
        self.stdout.write(self.style.SUCCESS(f'Done in {time.perf_counter() - start:.2f} seconds'))