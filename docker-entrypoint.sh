#!/bin/sh

set -e

sleep 1

/srv/env/bin/python /srv/app/manage.py migrate
/srv/env/bin/python /srv/app/manage.py load_plans
/srv/env/bin/python /srv/app/manage.py create_admin
/srv/env/bin/python /srv/app/manage.py create_server_size
/srv/env/bin/python /srv/app/manage.py site_host

exec "$@"
