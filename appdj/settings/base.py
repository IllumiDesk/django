"""
Django settings for appdj project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import dj_database_url
import datetime
import uuid
from appdj.settings import BASE_DIR
from appdj.settings.tbslog import TBS_LOGGING
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'test')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', "test secret key")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.sites',

    'channels',
    'rest_framework',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'storages',
    'django_extensions',
    'cacheops',
    'corsheaders',
    'guardian',
    'django_filters',
    'haystack',
    'djoser',
    'django_ses',
    'treebeard',

    'base',
    'notifications',
    'users',
    'billing',
    'projects',
    'servers',
    'actions',
    'infrastructure',
    'triggers',
    'jwt_auth',
    'search',
    'teams',
    'canvas',
]

MIDDLEWARE = [
    'jwt_auth.middleware.OAuthUIMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'actions.middleware.ActionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'base.middleware.NamespaceMiddleware',
    'billing.middleware.SubscriptionMiddleware'
]

ROOT_URLCONF = 'appdj.urls.base'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'appdj.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# Email Settings
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_ACCESS_KEY_ID = os.getenv("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = os.getenv("AWS_SES_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = os.getenv("AWS_SES_REGION_ENDPOINT")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '587')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, default='postgres://postgres:@localhost:5432/postgres')
}

# Channels

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL')],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
        "ROUTING": "appdj.routing.routing",
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.slack.SlackOAuth2',
    'users.backends.ActiveUserBackend',
    'guardian.backends.ObjectPermissionBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_CLIENT_ID', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive'
]

SOCIAL_AUTH_GITHUB_KEY = os.environ.get('GITHUB_CLIENT_ID', '')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email', 'repo']

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

HTTPS = os.environ.get("TBS_HTTPS", "false").lower() == "true"
LOGIN_URL = '/api-auth/login/'
LOGIN_REDIRECT_URL = '{scheme}://{host}/auth/token-login'.format(
    scheme='https' if HTTPS else 'http', host=os.environ.get('TBS_DOMAIN'))
LOGOUT_URL = '/api-auth/logout/'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

BCRYPT_LOG_ROUNDS = 13

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_ALLOW_REFRESH': True,
    'JWT_DECODE_HANDLER': 'jwt_auth.utils.jwt_decode_handler'
}
JWT_TMP_EXPIRATION_DELTA = datetime.timedelta(seconds=60)

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = os.environ.get('SITE_ID', 'c66d1616-09a7-4594-8c6d-2e1c1ba5fe3b')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
STATIC_URL = "https://{}/".format(AWS_S3_CUSTOM_DOMAIN)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID', '')
AWS_DEPLOYMENT_ROLE = os.environ.get('AWS_DEPLOYMENT_ROLE', '')
AWS_LAMBDA_AUTHORIZER = os.environ.get('AWS_LAMBDA_AUTHORIZER', '')
AWS_AUTHORIZER_ROLE = os.environ.get('AWS_AUTHORIZER_ROLE', '')
AWS_JOBS_ROLE = os.environ.get('AWS_JOBS_ROLE', '')

SWAGGER_SETTINGS = {
    'SUPPORTED_SUBMIT_METHODS': ['head', 'get', 'post', 'put', 'delete', 'patch']
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'teams.permissions.TeamGroupPermission',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'base.pagination.LimitOffsetPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
}

DJOSER = {
    'DOMAIN': os.getenv("TBS_DOMAIN"),
    'SITE_NAME': "IllumiDesk",
    'PASSWORD_RESET_CONFIRM_URL': "auth/password-reset?uid={uid}&token={token}",
    'SERIALIZERS': {'user': "users.serializers.UserSerializer",
                    'user_registration': "users.serializers.UserSerializer",
                    'token': "jwt_auth.serializers.JWTSerializer"},
    'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': "auth/activate?uid={uid}&token={token}"
}


DEFAULT_VERSION = os.environ.get('TBS_DEFAULT_VERSION', "v1")

RESOURCE_DIR = os.environ.get('RESOURCE_DIR', '/workspaces')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'SERIALIZER_CLASS': 'utils.UJSONSerializer',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5
        },
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CACHEOPS_REDIS = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

CACHEOPS = {
    # Automatically cache any User.objects.get() calls for 15 minutes
    # This includes request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60 * 60},

    # Cache gets, fetches, counts and exists to Permission
    # 'all' is just an alias for ('get', 'fetch', 'count', 'exists')
    'auth.permission': {'ops': 'all', 'timeout': 60 * 60},

    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    '*.*': {'timeout': 60 * 60},
}

CACHEOPS_DEGRADE_ON_FAILURE = True

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# celery
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_BROKER_POOL_LIMIT = 1  # Will decrease connection usage
CELERY_BROKER_HEARTBEAT = None  # We're using TCP keep-alive instead
CELERY_BROKER_CONNECTION_TIMEOUT = 30  # May require a long timeout due to Linux DNS timeouts etc
CELERY_SEND_EVENTS = False  # Will not create celeryev.* queues
CELERY_EVENT_QUEUE_EXPIRES = 60  # Will delete all celeryev. queues without consumers after 1 minute.
CELERY_BROKER_URL = os.environ.get('RABBITMQ_URL')
CELERY_REDBEAT_REDIS_URL = os.environ.get('REDIS_URL')
CELERY_BEAT_SCHEDULER = 'redbeat:RedBeatScheduler'
CELERY_BEAT_MAX_LOOP_INTERVAL = 60

USE_X_FORWARDED_HOST = True

PRIMARY_KEY_FIELD = ('django.db.models.UUIDField', dict(primary_key=True, default=uuid.uuid4, editable=False))

MIGRATION_MODULES = {
    'sites': 'appdj.migrations.sites',
    'admin': 'appdj.migrations.admin',
    'auth': 'appdj.migrations.auth',
    'contenttypes': 'appdj.migrations.contenttypes',
    'django_celery_results': 'appdj.migrations.django_celery_results',
    'oauth2_provider': 'appdj.migrations.oauth2_provider',
    'social_django': 'appdj.migrations.social_django',
    'guardian': 'appdj.migrations.guardian',
    'django_ses': 'appdj.migrations.django_ses',
}


# Server settings
SERVER_RESOURCE_DIR = os.environ.get("SERVER_RESOURCE_DIR", "/resources")
SERVER_PORT_MAPPING = {'8080': "proxy", '6006': 'restful'}
SERVER_TYPES = {"restful", "cron", "proxy", "batch"}
SERVER_TYPE_MAPPING = {'jupyter': 'proxy', 'rstudio': 'proxy'}
SERVER_ENDPOINT_URLS = {'restful': '/restful/', 'proxy': '/proxy/'}
SERVER_COMMANDS = {
    'jupyter': 'jupyter lab --NotebookApp.base_url=' +
    '"/{version}/{server.project.owner.username}/projects/{server.project.pk}/servers/{server.pk}/endpoint/proxy"',
    'rstudio': '/init',
}
# slack

SOCIAL_AUTH_SLACK_KEY = os.environ.get('SLACK_KEY')
SOCIAL_AUTH_SLACK_SECRET = os.environ.get('SLACK_SECRET')

# CORS requests
CORS_ORIGIN_ALLOW_ALL = True

LOGGING = TBS_LOGGING

ENABLE_BILLING = os.environ.get("ENABLE_BILLING", "false").lower() == "true"

# A list of url *names* that require a subscription to access.
SUBSCRIPTION_REQUIRED_URLS = ["server-start"]

# What should this setting actually be? They seem reasonable for dev environments
# But I'm not sure if they're secure and what not for prod
MEDIA_ROOT = "/workspaces/"
MEDIA_URL = "/media/"


es_url = os.environ.get("ELASTICSEARCH_URL",  "http://search:9200/")
es_use_ssl = "https://" in es_url

HAYSTACK_CONNECTIONS = {
    "default": {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': es_url,
        'INDEX_NAME': '3blades',
        'KWARGS': {
            'http_auth': (os.getenv("ELASTICSEARCH_USER"), os.getenv("ELASTICSEARCH_PASSWORD")),
            'use_ssl': es_use_ssl,
        }
    }
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

DOCKER_NET = os.environ.get('DOCKER_NET', 'tbs-net')

MOCK_STRIPE = os.environ.get("MOCK_STRIPE", "false").lower() == "true"

# KB * KB = MB -> 15 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * int(os.getenv("MAX_FILE_UPLOAD_SIZE", 15))

SILENCED_SYSTEM_CHECKS = ["auth.W004"]

DEFAULT_STRIPE_PLAN_ID = os.getenv("DEFAULT_STRIPE_PLAN_ID", "threeblades-free-plan")

NVIDIA_DOCKER_HOST = os.environ.get('NVIDIA_DOCKER_HOST')

SPAWNER = 'servers.spawners.ecs.ECSSpawner'
DEPLOYER = 'servers.spawners.aws_lambda.deployer.LambdaDeployer'
SCHEDULER = 'servers.spawners.ecs.JobScheduler'
ECS_CLUSTER = os.environ.get('ECS_CLUSTER', 'default')
BATCH_COMPUTE_ENV = os.environ.get('BATCH_COMPUTE_ENV')
BATCH_JOB_QUEUE = os.environ.get('BATCH_JOB_QUEUE')
REDIRECT_IS_HTTPS = True

# Default server memory sizes in MB, implemented in /servers/management/commands/
SERVER_SIZE = {
    "Nano": 512,
    "Small": 1024,
    "Medium": 2048,
    "Large": 4096
}

GETTING_STARTED_PROJECT = os.environ.get("GETTING_STARTED_PROJECT", "GettingStarted")

USAGE_WARNING_THRESHOLDS = os.environ.get("USAGE_WARNING_THRESHOLDS", "75,90,100")

BILLING_BUCKET_SIZE_GB = os.environ.get("BILLING_BUCKET_SIZE_GB", 5)

BUCKET_COST_USD = os.environ.get("BUCKET_COST_USD", 5)
