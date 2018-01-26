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

import hmac
from zope.interface import implementer
from armonaut.webhooks.interfaces import IWebhookVerifierService


def github_webhook_verifier_factory(context, request):
    return GithubWebhookVerifierService()


def gitlab_webhook_verifier_factory(context, request):
    return GitlabWebhookVerifierService()


def bitbucket_webhook_verifier_factory(context, request):
    return BitbucketWebhookVerifierService()


@implementer(IWebhookVerifierService)
class GithubWebhookVerifierService:
    def verify_webhook(self, request, secret):
        signature = request.headers.get('X-Hub-Signature')
        if signature is None:
            return False

        sigtype, signature = signature.split('=')

        # Did Github change their signature algorithm?
        if sigtype != 'sha1':
            return False

        mac = hmac.new(secret.decode('ascii'), msg=request.data, digestmod='sha1')
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            return False
        return True


@implementer(IWebhookVerifierService)
class GitlabWebhookVerifierService:
    def verify_webhook(self, request, secret):
        secret_token = request.headers.get('X-Gitlab-Token')
        if secret_token is None:
            return False

        if secret_token != secret:
            return False
        return True


@implementer(IWebhookVerifierService)
class BitbucketWebhookVerifierService:
    def verify_webhook(self, request, secret):
        return True
