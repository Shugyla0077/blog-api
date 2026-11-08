from pathlib import Path

from decouple import Config, Csv, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / 'settings' / '.env'

config = Config(RepositoryEnv(str(ENV_FILE_PATH)))

ENV_ID: str = config('BLOG_ENV_ID', default='local')
SECRET_KEY: str = config('BLOG_SECRET_KEY')
DEBUG: bool = config('BLOG_DEBUG', default=False, cast=bool)
ALLOWED_HOSTS: list[str] = config(
    'BLOG_ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv(),
)

DB_NAME: str = config('BLOG_DB_NAME', default='blog_db')
DB_USER: str = config('BLOG_DB_USER', default='postgres')
DB_PASSWORD: str = config('BLOG_DB_PASSWORD', default='postgres')
DB_HOST: str = config('BLOG_DB_HOST', default='127.0.0.1')
DB_PORT: int = config('BLOG_DB_PORT', default=5432, cast=int)