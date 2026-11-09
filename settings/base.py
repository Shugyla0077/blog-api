from django.urls import reverse_lazy

from settings.conf import ALLOWED_HOSTS as ALLOWED_HOSTS
from settings.conf import BASE_DIR as BASE_DIR
from settings.conf import SECRET_KEY as SECRET_KEY

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'apps.auths',
    'apps.blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'
AUTH_USER_MODEL = 'auths.User'

_PREFIX = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{_PREFIX}.UserAttributeSimilarityValidator'},
    {'NAME': f'{_PREFIX}.MinimumLengthValidator'},
    {'NAME': f'{_PREFIX}.CommonPasswordValidator'},
    {'NAME': f'{_PREFIX}.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    'SITE_TITLE': 'Blog Admin',
    'SITE_HEADER': 'Blog API',
    'SITE_SUBHEADER': 'Admin Panel',
    'SITE_SYMBOL': 'article',
    'ENVIRONMENT': 'apps.blog.callbacks.environment_callback',
    'DASHBOARD_CALLBACK': 'apps.blog.callbacks.dashboard_callback',
    'COMMAND': {'search_models': True},
    'SITE_DROPDOWN': [
        {'icon': 'code', 'title': 'GitHub', 'link': 'https://github.com/Shugyla0077/blog-api'},
        {'icon': 'book', 'title': 'Unfold Docs', 'link': 'https://unfoldadmin.com/docs/'},
    ],
    'COLORS': {
        'primary': {
            '50': '236 253 245',
            '100': '209 250 229',
            '200': '167 243 208',
            '300': '110 231 183',
            '400': '52 211 153',
            '500': '16 185 129',
            '600': '5 150 105',
            '700': '4 120 87',
            '800': '6 95 70',
            '900': '6 78 59',
            '950': '2 44 34',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'navigation': [
            {
                'title': 'Overview',
                'items': [
                    {'title': 'Dashboard', 'icon': 'dashboard', 'link': reverse_lazy('admin:index')},
                ],
            },
            {
                'title': 'Content',
                'items': [
                    {
                        'title': 'Posts',
                        'icon': 'article',
                        'link': reverse_lazy('admin:blog_post_changelist'),
                        'badge': 'apps.blog.callbacks.drafts_badge',
                    },
                    {'title': 'Comments', 'icon': 'chat', 'link': reverse_lazy('admin:blog_comment_changelist')},
                    {'title': 'Categories', 'icon': 'category', 'link': reverse_lazy('admin:blog_category_changelist')},
                    {'title': 'Tags', 'icon': 'sell', 'link': reverse_lazy('admin:blog_tag_changelist')},
                ],
            },
            {
                'title': 'Users & Access',
                'permission': lambda request: request.user.is_superuser,
                'items': [
                    {'title': 'Users', 'icon': 'person', 'link': reverse_lazy('admin:auths_user_changelist')},
                    {'title': 'Groups', 'icon': 'groups', 'link': reverse_lazy('admin:auth_group_changelist')},
                ],
            },
        ],
    },
    'TABS': [
        {
            'models': ['blog.post'],
            'items': [
                {'title': 'All', 'link': lambda req: str(reverse_lazy('admin:blog_post_changelist'))},
                {'title': 'Published', 'link': lambda req: f"{reverse_lazy('admin:blog_post_changelist')}?status=published"},
                {'title': 'Drafts', 'link': lambda req: f"{reverse_lazy('admin:blog_post_changelist')}?status=draft"},
            ],
        },
    ],
}