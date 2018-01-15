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
from armonaut.cache.http import cache_control


def test_cache_public():
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
