# IllumiDesk Django

## Dev Setup

### Requirements

- Docker Compose
- Docker CE

### Build Custom Frontend Assets

Build the front end assets:

    $ npm install
    $ npm run dev

You can also use the `npm run dev-watch` option to enable hot reloading. Use `npm run build` for production builds.

### Build and Run the Stack

Build and run the docker images in detached mode using the `docker-compose` command:

    $ docker-compose -f local.yml up -d --build

Generally, if you want to emulate production environment use `production.yml` instead. And this is true for any other actions you might need to perform: whenever a switch is required, just do it!

    $ docker-compose -f production.yml up -d --build

> **Note**: For those of you familiar with django's collectstatic and migrate commands, these are included as part of the docker image entry points.

### Create Admin User

As with any shell command that we wish to run in our container, this is done using the `docker-compose -f local.yml run --rm ...` command:

    $ docker-compose -f local.yml run --rm webapp python manage.py createsuperuser

## Setting Up Your Users

* When running tests the **test user accounts** are created with factory methods so only the test command is necessary to run tests that require user accounts.

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* You can create any number of **superuser accounts** which allows you to log into the `admin` console:

    $ docker-compose -f local.yml run --rm webapp python manage.py createsuperuser

### Type checks

    $ docker-compose -f local.yml run --rm webapp python mypy illumidesk

### Linters

    $ docker-compose -f local.yml run --rm webapp flake8 illumidesk
    $ docker-compose -f local.yml run --rm webapp pylint illumidesk

### Unit Tests

    $ docker-compose -f local.yml run --rm webapp pytest illumidesk

### Configuring the Environment

This is the excerpt from your project’s local.yml:

The most important thing for us here now is `env_file` section enlisting `./.envs/.local/.postgres`. Generally, the stack’s behavior is governed by a number of environment variables (env(s), for short) residing in envs/, for instance, this is what we generate for you:

```
.envs
├── .local
│   ├── .django
│   └── .postgres
└── .production
    ├── .django
    └── .postgres
```

By convention, `local.yml` corresponds to the development version and `production.yml` corresponds to the production version. The `.envs` folder contains the environment variable files within a folder named by the `*.yml` environment.

For example, the local environment variables for postgres are located in the aforementioned `.envs/.local/.postgres`:

```
# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=postgres
POSTGRES_DB=<your project slug>
POSTGRES_USER=XgOWtQtJecsAbaIyslwGvFvPawftNaqO
POSTGRES_PASSWORD=jSljDz4whHuwO3aJIgVBrqEml5Ycbghorep4uVJ4xjDYQu0LfuTZdctj7y0YcCLu
```

The three envs we are presented with here are `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. Should you ever need to merge .envs/production/* in a single .env run the merge_production_dotenvs_in_dotenv.py:

    $ python merge_production_dotenvs_in_dotenv.py

The .env file will then be created, with all your production envs residing beside each other.

### Debugging with `django-debug-toolbar`

In order for django-debug-toolbar to work designate your Docker Machine IP with INTERNAL_IPS in local.py.

### Mailhog

When developing locally you can go with MailHog for email testing provided use_mailhog was set to y on setup. To proceed,

1. make sure mailhog container is up and running;
2. open up http://127.0.0.1:8025.

### Celery tasks in local development

When not using docker Celery tasks are set to run in Eager mode, so that a full stack is not needed. When using docker the task scheduler will be used by default.

If you need tasks to be executed on the main thread during development set CELERY_TASK_ALWAYS_EAGER = True in config/settings/local.py.

Possible uses could be for testing, or ease of profiling with DJDT.

### Celery Flower

Flower is a “real-time monitor and web admin for Celery distributed task queue”.

By default, it’s enabled both in local and production environments (`local.yml` and `production.yml` Docker Compose configs, respectively) through a flower service. For added security, flower requires its clients to provide authentication credentials specified as the corresponding environments’ `.envs/.local/.django` and `.envs/.production/.django` `CELERY_FLOWER_USER` and `CELERY_FLOWER_PASSWORD` environment variables. By default, the flower services is exposed via port `5555`.
