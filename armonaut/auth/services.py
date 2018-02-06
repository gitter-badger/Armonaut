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

import redis
import functools
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer
from armonaut.auth.interfaces import (
    IUserService, IOAuthStateService
)
from armonaut.auth.models import User
from armonaut.utils import crypto


@implementer(IUserService)
class DatabaseUserService:
    def __init__(self, session):
        self.db = session

    @functools.lru_cache()
    def get_user(self, user_id):
        return self.db.query(User).get(user_id)

    @functools.lru_cache()
    def find_userid(self, username):
        try:
            user = (
                self.db.query(User.id)
                    .filter(User.username == username)
                    .one()
            )
        except NoResultFound:
            return None
        return user.id

    def create_user(self, username, display_name, access_token):
        user = User()
        user.username = username
        user.display_name = display_name
        user.access_token = access_token
        user.avatar_url = avatar_url

    def update_user(self, user_id, **changes):
        user = self.get_user(user_id)
        if user is None:
            return
        for name, value in changes.items():
            setattr(user, name, value)
        return user


@implementer(IOAuthStateService)
class RedisOAuthStateService:
    max_age = 5 * 60  # 5 minute expire time on state tokens.

    def __init__(self, url):
        self.redis = redis.StrictRedis.from_url(url)

    def create_state(self):
        state = crypto.random_token()
        self.redis.setex(self._redis_key(state), self.max_age, 1)
        return state

    def check_state(self, state):
        key = self._redis_key(state)
        found = self.redis.get(key)
        if found is None:
            return False
        self.redis.delete(key)
        return True

    @staticmethod
    def _redis_key(state):
        return f'armonaut/oauth/data/{state}'


def database_login_factory(context, request):
    return DatabaseUserService(
        request.db,
    )


def oauth_state_factory(context, request):
    return RedisOAuthStateService(
        request.registry.settings['oauth.url']
    )
