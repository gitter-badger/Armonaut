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
import pytest
from armonaut.events.tasks import send_event


@pytest.mark.parametrize('channels', ['channel-name', ['channel-1', 'channel-2']])
def test_send_event(channels):
    request = pretend.stub(
        pusher=pretend.stub(
            trigger=pretend.call_recorder(lambda *args, **kwargs: None)
        )
    )
    send_event(request, channels=channels, event='event-name', data={'key': 'value'})

    assert request.pusher.trigger.calls == [
        pretend.call(channels=channels,
                     event_name='event-name',
                     data={'key': 'value'})
    ]
