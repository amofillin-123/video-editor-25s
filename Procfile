web: gunicorn web_app:app
worker: celery -A web_app.celery worker --loglevel=info
