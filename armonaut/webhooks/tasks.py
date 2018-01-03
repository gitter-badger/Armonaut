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

from flask import Request
from armonaut.celery import celery


@celery.task(ignore_result=True)
def process_github_webhook(request: Request):
    raise NotImplementedError()


@celery.task(ignore_result=True)
def process_gitlab_webhook(request: Request):
    raise NotImplementedError()


@celery.task(ignore_result=True)
def process_bitbucket_webhook(request: Request):
    raise NotImplementedError()
