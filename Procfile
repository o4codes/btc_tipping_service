
release: python manage.py migrate
web: gunicorn api.core.wsgi --timeout=30 --log-file -
