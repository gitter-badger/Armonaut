release: python -m armonaut db upgrade
web: gunicorn --bind 0.0.0.0:8080 armonaut.wsgi:app
worker: celery -A armonaut.celery.app worker -B -S redbeat.RedBeatScheduler -l info
