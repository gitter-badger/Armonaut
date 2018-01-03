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

import os


class BaseConfig(object):
    SECRET_KEY = os.environ['SECRET_KEY']

    REDIS_URL = os.environ['REDIS_URL']
    RABBITMQ_URL = os.environ['RABBITMQ_URL']
    DATABASE_URL = os.environ['DATABASE_URL']

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'

    CELERY_BROKER_URL = RABBITMQ_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    CACHE_CONTROL_ENABLED = True
    FASTLY_ENABLED = True


class DevelopmentConfig(BaseConfig):
    PORT = 8080
    DEBUG = True
    RATELIMIT_ENABLED = False
    FASTLY_ENABLED = False


class ProductionConfig(BaseConfig):
    PORT = 80
    DEBUG = False
