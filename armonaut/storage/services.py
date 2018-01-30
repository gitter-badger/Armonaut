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

import boto3.session
from zope.interface import implementer
from armonaut.storage.interfaces import IObjectStorage


def spaces_session_factory(context, request):
    kwargs = {}

    if request.registry.settings.get('spaces.region') is not None:
        kwargs['region_name'] = request.registry.settings['spaces.region']

    return boto3.session.Session(
        endpoint_url='https://nyc3.digitaloceanspaces.com',
        aws_access_key_id=request.registry.settings['spaces.api_id'],
        aws_secret_access_key=request.registry.settings['spaces.api_secret'],
        **kwargs
    )


@implementer(IObjectStorage)
class SpacesObjectStorage:
    def __init__(self, bucket, session):
        self.bucket = bucket
        self.session = session

    @classmethod
    def create_service(cls, context, request):
        return cls(
            request.registry.settings['spaces.bucket'],
            request.find_service(name='spaces.session')
        )

    def create_presigned_url(self, method, path, expires_in):
        return self.session.generate_presigned_url(
            ClientMethod=method,
            Params={
                'Bucket': self.bucket,
                'Key': path
            },
            ExpiresIn=expires_in
        )
