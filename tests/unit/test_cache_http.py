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

import pytest
import pretend
from armonaut.cache.http import (cache_control, add_vary,
                                 conditional_http_tween_factory, includeme)


def test_cache_public():
    """Assert that @cache_control(public=True) makes the
    Cache-Control header public.
    """
    response = pretend.stub(
        cache_control=pretend.stub(public=None, private=None, max_age=None)
    )
    request = pretend.stub(registry=pretend.stub(settings={}))
    context = pretend.stub()

    @cache_control(12)
    def view(ctx, req):
        assert context is ctx
        assert request is req
        return response

    resp = view(context, request)

    assert response is resp
    assert response.cache_control.public
    assert response.cache_control.max_age == 12
    assert response.cache_control.private is None


def test_cache_private():
    """Assert that @cache_control(public=False) makes
    the Cache-Control header private.
    """
    response = pretend.stub(
        cache_control=pretend.stub(private=None, public=None, max_age=None)
    )
    request = pretend.stub(registry=pretend.stub(settings={}))
    context = pretend.stub()

    @cache_control(6, public=False)
    def view(ctx, req):
        assert context is ctx
        assert request is req
        return response

    resp = view(context, request)

    assert response is resp
    assert response.cache_control.private
    assert response.cache_control.max_age == 6
    assert response.cache_control.public is None


def test_no_cache():
    """Assert that the @cache_control(False) decorator
    forces HTTP no-cache, etc
    """
    response = pretend.stub(
        cache_control=pretend.stub(
            no_cache=None,
            no_store=None,
            must_revalidate=None
        )
    )
    request = pretend.stub(registry=pretend.stub(settings={}))
    context = pretend.stub()

    @cache_control(False)
    def view(ctx, req):
        assert context is ctx
        assert request is req
        return response

    resp = view(context, request)

    assert response is resp
    assert response.cache_control.no_cache
    assert response.cache_control.no_store
    assert response.cache_control.must_revalidate


def test_prevent_http_cache():
    """Assert that the pyramid.prevent_http_cache setting
    disables the cache.
    """
    response = pretend.stub(
        cache_control=pretend.stub()
    )
    request = pretend.stub(
        registry=pretend.stub(settings={
            'pyramid.prevent_http_cache': True
        })
    )
    context = pretend.stub()

    @cache_control(12)
    def view(ctx, req):
        assert context is ctx
        assert request is req
        return response

    resp = view(context, request)

    assert response is resp


@pytest.mark.parametrize(
    'vary',
    [None,
     [],
     ['bar'],
     ['foo', 'bar'],
     ['foobar']]
)
def test_add_vary(vary):
    """Assert that the add_vary() directive correctly adds
    a non-duplicate value to the Vary HTTP header."""
    class FakeRequest:
        def __init__(self):
            self.callbacks = []

        def add_response_callback(self, callback):
            self.callbacks.append(callback)

    request = FakeRequest()
    context = pretend.stub()
    response = pretend.stub(vary=vary)

    def view(context, request):
        return response

    assert add_vary('foobar')(view)(context, request) is response
    assert len(request.callbacks) == 1

    request.callbacks[0](request, response)

    if vary is None:
        vary = []

    assert response.vary == {'foobar'} | set(vary)


def test_has_last_modified():
    """Asserts that if a Last-Modified header is defined in the HTTP response
    that the response will be marked with response.conditional_response.
    """
    response = pretend.stub(
        last_modified=pretend.stub(),
        status_code=200,
        etag=None,
        conditional_response=False,
        app_iter=iter([b'foo']),
        content_length=None
    )

    request = pretend.stub(method='GET')
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.conditional_response


def test_explicit_etag():
    """Asserts that if an Etag header is defined in the HTTP response
    that the response will be marked with response.conditional_response
    """
    response = pretend.stub(
        last_modified=None,
        etag='foo',
        conditional_response=False,
        app_iter=iter([b'foo'])
    )
    request = pretend.stub(method='GET')
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.conditional_response


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_implicit_etag(method):
    """Asserts that if a response isn't streamed and doesn't have an ETag
    header that the ETag will be calculated and the response will be
    marked with response.conditional_response
    """
    response = pretend.stub(
        last_modified=None,
        etag=None,
        conditional_response=False,
        md5_etag=pretend.call_recorder(lambda: None),
        app_iter=[b'foo'],
        content_length=None,
        status_code=200
    )

    request = pretend.stub(method=method)
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.md5_etag.calls == [pretend.call()]
    assert response.conditional_response


def test_implicit_etag_buffers_streaming():
    """Asserts that if a response is meant to be streamed but is under
    the BUFFER_MAX limit then the response body will be buffered and
    an ETag will be calculated.
    """
    response = pretend.stub(
        last_modified=None,
        etag=None,
        conditional_response=False,
        md5_etag=pretend.call_recorder(lambda: None),
        app_iter=iter([b'foo']),
        content_length=3,
        body=b'foo',
        status_code=200
    )

    request = pretend.stub(method='GET')
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.md5_etag.calls == [pretend.call()]
    assert response.conditional_response


def test_no_implicit_etag_not_200():
    """Asserts that if the status code of the response isn't 200 then
    it won't have an ETag calculated.
    """
    response = pretend.stub(
        last_modified=None,
        etag=None,
        conditional_response=False,
        md5_etag=pretend.call_recorder(lambda: None),
        app_iter=[b'foo'],
        status_code=201
    )

    request = pretend.stub(method="GET")
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.md5_etag.calls == []
    assert not response.conditional_response


@pytest.mark.parametrize('method', ['PUT', 'POST'])
def test_no_implicit_etag_wrong_method(method):
    """Asserts that if the method isn't GET or HEAD
    then an ETag won't be calculated.
    """
    response = pretend.stub(
        last_modified=None,
        etag=None,
        conditional_response=False,
        md5_etag=pretend.call_recorder(lambda: None),
        app_iter=[b'foo'],
        status_code=200
    )

    request = pretend.stub(method=method)
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.md5_etag.calls == []
    assert not response.conditional_response


def test_no_etag_if_streaming_without_content_length():
    """Asserts that if the response is streamed but doens't
    define a Content-Length header then we can't calculate
    an ETag header.
    """
    response = pretend.stub(
        last_modified=None,
        etag=None,
        conditional_response=False,
        md5_etag=pretend.call_recorder(lambda: None),
        app_iter=iter([b'foo']),
        content_length=None,
        status_code=200
    )

    request = pretend.stub(method='GET')
    handler = pretend.call_recorder(lambda request: response)

    tween = conditional_http_tween_factory(handler, pretend.stub())

    assert tween(request) is response
    assert handler.calls == [pretend.call(request)]
    assert response.md5_etag.calls == []
    assert not response.conditional_response


def test_includeme():
    config = pretend.stub(
        add_tween=pretend.call_recorder(lambda t: None)
    )
    includeme(config)

    assert config.add_tween.calls == [
        pretend.call('armonaut.cache.http.conditional_http_tween_factory')
    ]
