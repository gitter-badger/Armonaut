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
from zope.interface.verify import verifyClass
from armonaut.storage.interfaces import IObjectStorage
from armonaut.storage.services import SpacesObjectStorage


def test_verify_service():
    assert verifyClass(IObjectStorage, SpacesObjectStorage)


def test_object_storage_init():
    bucket = 'bucket'
    session = pretend.stub()

    storage = SpacesObjectStorage(bucket, session)

    assert storage.bucket == bucket
    assert storage.session is session


def test_create_service():
    session = pretend.stub()
    request = pretend.stub(
        find_service=pretend.call_recorder(lambda name: session),
        registry=pretend.stub(settings={'spaces.bucket': 'armonaut'})
    )
    storage = SpacesObjectStorage.create_service(None, request)

    assert request.find_service.calls == [pretend.call(name='spaces.session')]
    assert storage.bucket == 'armonaut'


def test_create_presigned_url():
    session = pretend.stub(
        generate_presigned_url=pretend.call_recorder(lambda *args, **kwargs: 'presigned-url')
    )
    request = pretend.stub(
        find_service=pretend.call_recorder(lambda name: session),
        registry=pretend.stub(settings={'spaces.bucket': 'armonaut'})
    )
    storage = SpacesObjectStorage.create_service(None, request)

    presigned_url = storage.create_presigned_url(method='get_object', path='test/object', expires_in=300)

    assert presigned_url == 'presigned-url'
    assert session.generate_presigned_url.calls == [pretend.call(
        ClientMethod='get_object',
        Params={'Bucket': 'armonaut', 'Key': 'test/object'},
        ExpiresIn=300
    )]
