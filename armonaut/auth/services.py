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
    IUserService, IOAuthService
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

    def update_user(self, user_id, **changes):
        user = self.get_user(user_id)
        if user is None:
            return
        for name, value in changes.items():
            setattr(user, name, value)
        return user

    def get_user_from_access_token(self, request, access_token):
        with request.http.get('https://api.github.com/user',
                              headers={'Authorization': f'token {access_token}'}) as r:
            if not r.ok:
                return None
            user_json = r.json()
            try:
                user = (
                    self.db.query(User.id)
                        .filter(User.github_id == user_json['id'])
                        .one()
                )

            # No user found but we have a valid access token
            # so we should create a new user.
            except NoResultFound:
                user = User()
                user.github_id = user_json['id']

            # Otherwise take the opportunity to update to latest information.
            user.username = user_json['login']
            user.avatar_url = user_json['avatar_url']
            user.display_name = user_json['name']
            user.access_token = access_token

            request.db.add(user)
            request.db.flush()

            return user


@implementer(IOAuthService)
class RedisOAuthService:
    max_state_age = 5 * 60  # 5 minute expire time on state tokens.

    def __init__(self, url, client_id, client_secret):
        self.redis = redis.StrictRedis.from_url(url)
        self._client_id = client_id
        self._client_secret = client_secret

    def create_state(self):
        state = crypto.random_token()
        self.redis.setex(self._redis_key(state), self.max_state_age, 1)
        return state

    def check_state(self, state):
        key = self._redis_key(state)
        found = self.redis.get(key)
        if found is None:
            return False
        self.redis.delete(key)
        return True

    def exchange_code_for_access_token(self, request, code, state):
        with request.http.post('https://github.com/login/oauth/access_token',
                               params={'client_id': self._client_id,
                                       'client_secret': self._client_secret,
                                       'code': code,
                                       'state': state,
                                       'redirect_uri': request.route_url('auth.callback')}) as r:
            if not r.ok:
                return None
            try:
                return r.json()['access_token']
            except KeyError:
                return None

    @staticmethod
    def _redis_key(state):
        return f'armonaut/oauth/data/{state}'


def database_login_factory(context, request):
    return DatabaseUserService(
        request.db,
    )


def oauth_factory(context, request):
    return RedisOAuthService(
        request.registry.settings['oauth.state_storage_url'],
        request.registry.settings['oauth.client_id'],
        request.registry.settings['oauth.client_secret']
    )
