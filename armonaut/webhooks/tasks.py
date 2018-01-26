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
from armonaut import tasks


@tasks.task(ignore_result=True, acks_late=True)
def process_github_webhook(request):

    secret = ''  # TODO: Get the webhook secret from project.

    # Verify the HMAC Signature against the webhook secret
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        return False

    sigtype, signature = signature.split('=')

    # Did Github change their signature algorithm?
    if sigtype != 'sha1':
        return False

    mac = hmac.new(secret.encode('ascii'), msg=request.data, digestmod='sha1')
    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        return False
