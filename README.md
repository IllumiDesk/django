[![Build Status](https://travis-ci.org/3Blades/app-backend.svg?branch=master)](https://travis-ci.org/3Blades/app-backend)
[![Docker Hub](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/3blades/app-backend/)
[![codecov](https://codecov.io/gh/3Blades/app-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/3Blades/app-backend)
[![Code Climate](https://codeclimate.com/github/3Blades/app-backend/badges/gpa.svg)](https://codeclimate.com/github/3Blades/app-backend)
[![Code Health](https://landscape.io/github/3Blades/app-backend/master/landscape.svg?style=flat)](https://landscape.io/github/3Blades/app-backend/master)
[![Requirements Status](https://requires.io/github/3Blades/app-backend/requirements.svg?branch=master)](https://requires.io/github/3Blades/app-backend/requirements/?branch=master)
[![slack in](https://slackin-pypmyuhqds.now.sh/badge.svg)](https://slackin-pypmyuhqds.now.sh/)

# 3Blades Backend Server
#

Application server backend based on [Django](https://www.djangoproject.com/).

Refer to [docs repo](https://github.com/3blades/docs) for full stack installation instructions.

## Dev Setup

Requirements:

- [Python 3.6](https://www.python.org/downloads/release/python-360/)
- [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- (Optional) [Docker](https://docs.docker.com/engine/installation/)

> Pro Tip! Use [pyenv](https://github.com/pyenv/pyenv) to install Python 3.6 on Linux systems.

We recommend using [Docker](https://docs.docker.com/engine/installation/) to run [Postgres](https://hub.docker.com/_/postgres/) and [Redis](https://hub.docker.com/_/redis/).

If you prefer, you can install [Postgres](https://www.postgresql.org/docs/current/static/tutorial-install.html) and [Redis](https://redis.io/topics/quickstart) directly on your host.

Configure virtualenv:

    virtualenv -p python3.6 venv
    source venv/bin/activate

Install dev dependencies:

    pip install -r ./requirements/dev.txt

(Optional) Run Postgres with docker:

    docker run --name my-postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres

(Optional) Run Redis with docker:

    docker run --name my-redis -p 6379:6379 -d redis

Verify docker containers:

```
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
e6c4011e0c3e        redis               "docker-entrypoint..."   4 seconds ago       Up 2 seconds        0.0.0.0:6379->6379/tcp   my-redis
057c41df17c8        postgres            "docker-entrypoint..."   12 seconds ago      Up 10 seconds       0.0.0.0:5432->5432/tcp   my-postgres
```

Export environment variables: `DATABASE_URL`, `REDIS_URL`, `DJANGO_SETTINGS_MODULE=appdj.settings.dev`. For example:

    export DATABASE_URL='postgres://postgres:mysecretpassword@localhost:5432/postgres'
    export REDIS_URL='redis://localhost:6379/0'
    export DJANGO_SETTINGS_MODULE='appdj.settings.dev'

Run database migrations:

    python manage.py migrate

Create admin (superuser) user:

    python manage.py createsuperuser

Run application:

    python manage.py runserver

Access API docs page and login:

    http://localhost:8000/swagger/

## Run Tests

Update Django settings so that it uses `test` module:

    export DJANGO_SETTINGS_MODULE=appdj.settings.test

Run tests:

    python manage.py test

## Swagger JSON file

http://127.0.0.1:8000/swagger/?format=openapi

## Contributing

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind
and build a nice open source community with us.


## Copyright and license

Copyright © 2016-2017 3Blades, LLC. All rights reserved, except as follows. Code
is released under the BSD 3.0 license. The README.md file, and files in the
"docs" folder are licensed under the Creative Commons Attribution 4.0
International License under the terms and conditions set forth in the file
"LICENSE.docs". You may obtain a duplicate copy of the same license, titled
CC-BY-SA-4.0, at http://creativecommons.org/licenses/by/4.0/.
