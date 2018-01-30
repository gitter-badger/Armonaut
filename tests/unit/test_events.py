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

import pretend
import pusher
from armonaut.events import includeme, _pusher


def test_includeme(monkeypatch):
    pusher_obj = pretend.stub()
    pusher_cls = pretend.call_recorder(lambda *args, **kwargs: pusher_obj)
    monkeypatch.setattr(pusher, 'Pusher', pusher_cls)

    config = pretend.stub(
        settings={
            'pusher.app_id': 'APP_ID',
            'pusher.api_id': 'API_ID',
            'pusher.api_secret': 'API_SECRET',
            'pusher.region': 'REGION'
        },
        registry={},
        add_request_method=pretend.call_recorder(lambda *args, **kwargs: None)
    )

    includeme(config)

    assert config.registry == {'pusher.client': pusher_obj}
    assert pusher_cls.calls == [pretend.call(
        app_id='APP_ID',
        key='API_ID',
        secret='API_SECRET',
        cluster='REGION'
    )]
    assert config.add_request_method.calls == [pretend.call(_pusher, name='pusher', reify=True)]
