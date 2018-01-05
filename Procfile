web: gunicorn -bind 0.0.0.0:8080 armonaut.wsgi:app
worker: celery worker -A armonaut.worker.celery -B -S redbeat.RedBeatScheduler -l info
