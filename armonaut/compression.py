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

import base64
import hashlib
from collections.abc import Sequence


ENCODINGS = ['gzip', 'identity']
BUFFER_MAX = 1 * 1024 * 1024


def _compressor(request, response):

    # Skip items with Vary: Cookie/Authorization for safety from CRIME.
    if (response.vary is not None and
            set(response.vary) & {'Cookie', 'Authorization'}):
        return

    # Content is already compressed or encoded.
    if 'Content-Encoding' in response.headers:
        return

    # Ensure that Accept-Encoding header gets added to the response.
    vary = set(response.vary if response.vary is not None else [])
    vary.add('Accept-Encoding')
    response.vary = vary

    target_encoding = request.accept_encoding.best_match(
        ENCODINGS, default_match='identity'
    )

    streaming = not isinstance(response.app_iter, Sequence)

    # If we are streaming a small amount of
    # content buffer the stream in memory
    if (streaming and response.content_length is not None and
            response.content_length <= BUFFER_MAX):
        _ = response.body  # Access the body attribute to collapse the stream
        streaming = False

    if streaming:
        response.encode_content(encoding=target_encoding, lazy=True)
        response.content_length = None

        if response.etag is not None:
            md5_digest = hashlib.md5((response.etag + ';gzip').encode('utf8'))
            md5_digest = md5_digest.digest()
            md5_digest = base64.b64encode(md5_digest)
            md5_digest = md5_digest.replace(b'\n', b'').decode('utf8')
            response.etag = md5_digest.strip('=')
    else:
        original_length = len(response.body)
        response.encode_content(encoding=target_encoding, lazy=False)

        if original_length < len(response.body):
            response.decode_content()

        if response.content_encoding is not None:
            response.md5_etag()


def compression_tween_factory(handler, _):
    def compression_tween(request):
        response = handler(request)

        # Use add_response_callback so that we can be sure that all other
        # response callbacks have been called already to use Vary headers.
        request.add_response_callback(_compressor)
        return response

    return compression_tween
