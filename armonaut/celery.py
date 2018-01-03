# Copyright 2018 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from celery import Celery
from armonaut import create_app


def create_celery(app) -> Celery:
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    base_task = celery.Task

    class ContextTask(base_task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return base_task.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_app()
celery = create_celery(app)
