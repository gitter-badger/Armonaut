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

import typing
from first import first
from datetime import datetime, timezone, timedelta
from limits import parse_many
from limits.strategies import MovingWindowRateLimiter
from limits.storage import storage_from_string
from zope.interface import implementer
from armonaut.rate_limit.interfaces import IRateLimiter


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


@implementer(IRateLimiter)
class DummyRateLimiter:
    def test(self, *identifiers):
        return True

    def hit(self, *identifiers):
        return True

    def resets_in(self, *identifiers):
        return None


class RateLimit(object):
    def __init__(self, limit, identifiers=None, limiter_class=RateLimiter):
        self.limit = limit
        self.identifiers = identifiers
        self.limiter_class = limiter_class

    def __call__(self, context, request):
        return self.limiter_class(
            request.registry['ratelimit.storage'],
            self.limit,
            self.identifiers
        )


def includeme(config):
    config.registry['ratelimit.storage'] = storage_from_string(
        config.registry.settings['ratelimit.url']
    )
