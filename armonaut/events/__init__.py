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

import pusher

EVENT_NEW_BUILD = 'new-build'
EVENT_JOB_STATUS = 'job-status'
EVENT_BUILD_STATUS = 'build-status'


def _pusher(request):
    return request.registry['pusher.client']


def includeme(config):
    client = pusher.Pusher(
        app_id=config.registry.settings['pusher.app_id'],
        key=config.registry.settings['pusher.api_id'],
        secret=config.registry.settings['pusher.api_secret'],
        cluster=config.registry.settings['pusher.region']
    )
    config.registry['pusher.client'] = client

    config.add_request_method(_pusher, name='pusher', reify=True)
