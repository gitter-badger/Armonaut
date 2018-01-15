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
import time
from armonaut.utils import crypto
from armonaut.sessions import InvalidSession, Session


@pytest.mark.parametrize(
    'method',
    ['__contains__',
     '__delitem__',
     '__getitem__',
     '__len__',
     '__iter__',
     '__setitem__',
     'clear',
     'copy',
     'fromkeys',
     'get',
     'items',
     'keys',
     'pop',
     'popitem',
     'setdefault',
     'update',
     'values',
     'invalidate',
     'flash',
     'changed',
     'get_csrf_token',
     'new_csrf_token',
     'pop_flash',
     'should_save']
)
def test_invalid_session_methods(method):
    """Assert that InvalidSession can't have any methods
    called without an exception being raised.
    """
    session = InvalidSession()
    with pytest.raises(RuntimeError):
        getattr(session, method)()


@pytest.mark.parametrize(
    'prop',
    ['sid', 'created', 'new']
)
def test_invalid_session_properties(prop):
    """Assert that InvalidSession can't have any properties
    read without an exception being raised."""
    session = InvalidSession()
    with pytest.raises(RuntimeError):
        getattr(session, prop)


def test_create_new_timestamp(monkeypatch):
    """Assert that session.created is the UTC timestamp
    that it was created on.
    """
    monkeypatch.setattr(time, 'time', lambda: 100)

    session = Session({})

    assert session.created == 100


@pytest.mark.parametrize(
    ('data', 'expected'),
    [(None, {}),
     ({}, {}),
     ({'foo': 'bar'}, {'foo': 'bar'})]
)
def test_create_new_session_id(monkeypatch, data, expected):
    """Assert that when a new session is created that
    it's properties are correctly set.
    """
    monkeypatch.setattr(crypto, 'random_token', lambda: '12345678')

    session = Session(data)
    assert session == expected
    assert session.sid == '12345678'
    assert session.new
    assert not session.invalidated


def test_new_session_not_changed():
    """Assert that a session should not be saved on
    creation without modifications.
    """
    session = Session({'foo': 'bar'})

    assert not session.should_save()


@pytest.mark.parametrize(
    ('func', 'args', 'changed', 'expected'),
    [('__getitem__', ('foo',), False, {'foo': 'bar'}),
     ('__setitem__', ('foo', 'bar'), False, {'foo': 'bar'}),
     ('__setitem__', ('foo', 'bel'), True, {'foo': 'bel'}),
     ('__setitem__', ('bar', 'foo'), True, {'bar': 'foo', 'foo': 'bar'}),
     ('__delitem__', ('foo',), True, {}),
     ('setdefault', ('foo', 'bar'), False, {'foo': 'bar'}),
     ('setdefault', ('foo', 'bel'), False, {'foo': 'bar'}),
     ('setdefault', ('bar', 'foo'), True, {'foo': 'bar', 'bar': 'foo'})]
)
def test_session_changed(func, args, changed, expected):
    """Assert that if a session is changed that it should be saved and
    that the modifications occur correctly.
    """
    session = Session({'foo': 'bar'})
    getattr(session, func)(*args)

    assert session.should_save() == changed
    assert session == expected
