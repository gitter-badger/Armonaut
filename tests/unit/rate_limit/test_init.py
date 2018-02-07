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
from armonaut.rate_limit import RateLimit, RateLimiter
from armonaut import rate_limit


def test_rate_limiter_init(monkeypatch):
    window_obj = pretend.stub()
    window_cls = pretend.call_recorder(lambda *args, **kwargs: window_obj)
    monkeypatch.setattr(rate_limit, 'MovingWindowRateLimiter', window_cls)
    storage = pretend.stub()
    limits = pretend.stub()
    parse_many = pretend.call_recorder(lambda lmts: limits)
    monkeypatch.setattr(rate_limit, 'parse_many', parse_many)

    rate_limiter = RateLimiter(storage, '1/minute', ['abc'])

    assert rate_limiter._identifiers == ['abc']
    assert rate_limiter._window is window_obj
    assert rate_limiter._limits == limits

    assert parse_many.calls == [pretend.call('1/minute')]
    assert window_cls.calls == [pretend.call(storage)]


def test_rate_limiter_empty_identifiers(monkeypatch):
    window_obj = pretend.stub()
    window_cls = pretend.call_recorder(lambda *args, **kwargs: window_obj)
    monkeypatch.setattr(rate_limit, 'MovingWindowRateLimiter', window_cls)
    storage = pretend.stub()
    limits = pretend.stub()
    parse_many = pretend.call_recorder(lambda lmts: limits)
    monkeypatch.setattr(rate_limit, 'parse_many', parse_many)

    rate_limiter = RateLimiter(storage, '1/minute')

    assert rate_limiter._identifiers == []
    assert rate_limiter._window is window_obj
    assert rate_limiter._limits == limits

    assert parse_many.calls == [pretend.call('1/minute')]
    assert window_cls.calls == [pretend.call(storage)]


def test_rate_limit():
    limiter_obj = pretend.stub()
    limiter_cls = pretend.call_recorder(lambda *args, **kwargs: limiter_obj)

    ratelimit = RateLimit(
        '1 per 5 minutes',
        identifiers=['abc'],
        limiter_class=limiter_cls
    )

    context = pretend.stub()
    request = pretend.stub(
        registry={'ratelimit.storage': pretend.stub()}
    )

    result = ratelimit(context, request)

    assert result is limiter_obj
    assert limiter_cls.calls == [pretend.call(
        request.registry['ratelimit.storage'],
        '1 per 5 minutes',
        ['abc']
    )]

"""
@implementer(IRateLimiter)
class RateLimiter:
    def __init__(self, storage, limit, identifiers=None):
        if identifiers is None:
            identifiers = []

        self._identifiers = [str(x) for x in identifiers]
        self._window = MovingWindowRateLimiter(storage)
        self._limits = parse_many(limit)

    def _get_identifiers(self, identifiers):
        return self._identifiers + [str(x) for x in identifiers]

    def hit(self, *identifiers):
        return all([
            self._window.hit(limit, *self._get_identifiers(identifiers))
            for limit in self._limits
        ])

    def test(self, *identifiers):
        return all([
            self._window.test(limit, *self._get_identifiers(identifiers))
            for limit in self._limits
        ])

    def resets_in(self, *identifiers) -> typing.Optional[timedelta]:
        resets = []
        identifiers = self._get_identifiers(identifiers)
        for limit in self._limits:
            resets_at, remaining = self._window.get_window_stats(limit, *identifiers)
            if remaining > 0:
                continue

            current = datetime.now(tz=timezone.utc)
            reset = datetime.utcfromtimestamp(resets_at)

            # If the current time is greater than the resets time we will skip for now
            # because it's either already resets or resetting now.
            if current > reset:
                continue

            resets.append(reset - current)

        return first(sorted(resets))
"""