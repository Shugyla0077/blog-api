MAX_CATEGORY_NAME_LENGTH: int = 100
MAX_TAG_NAME_LENGTH: int = 50
MAX_POST_TITLE_LENGTH: int = 200
MAX_POST_STATUS_LENGTH: int = 20

DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500
SEED_PASSWORD = 'password123'


SHORT_BODY_LEN = 50
COMMENTS_PER_PAGE = 10
TOP_AUTHORS_COUNT = 5

CATEGORIES = (
    'Python', 'Django', 'DevOps', 'Databases',
    'Frontend', 'Security', 'Testing', 'Architecture',
)
TAGS = (
  'api', 'rest', 'postgres', 'docker', 'linux', 'jwt', 'orm', 'celery',
  'redis', 'pytest', 'git', 'nginx', 'async', 'react', 'clean-code',
  'cloud', 'ci-cd', 'graphql', 'caching', 'deploy',
)