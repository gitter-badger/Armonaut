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

from flask import Blueprint, request
from armonaut.webhooks.tasks import (process_github_webhook,
                                     process_gitlab_webhook,
                                     process_bitbucket_webhook)

webhooks_blueprint = Blueprint('webhooks', __name__, url_prefix='/webhooks')


@webhooks_blueprint.route('/github', methods=['POST'])
def github_webhook():
    process_github_webhook.delay(request)


@webhooks_blueprint.route('/gitlab', methods=['POST'])
def gitlab_webhook():
    process_gitlab_webhook.delay(request)


@webhooks_blueprint.route('/bitbucket', methods=['POST'])
def bitbucket_webhook():
    process_bitbucket_webhook.delay(request)
