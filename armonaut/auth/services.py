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

import functools
import collections
from passlib.context import CryptContext
from zope.interface import implementer
from armonaut.auth.interfaces import (
    IUserService,
    IUserTokenService,
    InvalidPasswordResetToken
)
from armonaut.auth.models import User
from armonaut.rate_limit import DummyRateLimiter
from armonaut.utils.crypto import URLSafeSerializer, SignatureExpired, BadData
from armonaut.rate_limit.interfaces import IRateLimiter
from sqlalchemy.orm.exc import NoResultFound


@implementer(IUserService)
class DatabaseUserService:
    def __init__(self, session, rate_limiters=None):
        if rate_limiters is None:
            rate_limiters = {}

        self.db = session
        self.rate_limiters = collections.defaultdict(
            DummyRateLimiter,
            rate_limiters
        )
        self.hasher = CryptContext(
            schemes=['argon2'],
            deprecated='auto',
            truncate_error=False,

            argon2__memory_cost=1024,
            argon2__parallelism=6,
            argon2__time_cost=6
        )

    @functools.lru_cache()
    def get_user(self, user_id):
        return self.db.query(User).get(user_id)

    @functools.lru_cache()
    def find_userid(self, email):
        try:
            user = (
                self.db.query(User.id)
                    .filter(User.email == email)
                    .one()
            )
        except NoResultFound:
            return None
        return user.id

    def check_password(self, email, password):
        user = self.find_user(email)
        if user is not None:
            ok, new_hash = self.hasher.verify_and_update(
                password,
                user.password
            )
            if ok:
                if new_hash:
                    user.password = new_hash
                return True

        # On a failed attempt
        if user is not None:
            self.rate_limiters['user'].hit(user.id)
        self.rate_limiters['global'].hit()

        return False

    def create_user(self, email, password):
        user = User(email=email,
                    password=self.hasher.hash(password))
        self.db.add(user)
        self.db.flush()

    def update_user(self, user_id, **changes):
        user = self.get_user(user_id)
        if user is None:
            return
        for name, value in changes.items():
            if name == 'password':
                value = self.hasher.hash(value)
            setattr(user, name, value)
        return user

    def verify_user(self, email):
        user = self.find_user(email)
        if user is not None:
            user.email_verified = True


@implementer(IUserTokenService)
class UserTokenService:
    def __init__(self, user_service, settings):
        self.user_service = user_service
        self.serializer = URLSafeSerializer(
            settings['password_reset.secret'],
            salt='password-reset'
        )
        self.token_max_age = settings['password_reset.token_max_age']

    def generate_token(self, user):
        return self.serializer.dumps({
            'user.id': str(user.id),
            'user.last_login': str(user.last_login),
            'user.password_date': str(user.password_date)
        })

    def get_user_by_token(self, token):
        try:
            data = self.serializer.loads(token, max_age=self.token_max_age)
        except SignatureExpired:
            raise InvalidPasswordResetToken(
                'Invalid token - Token is expired, request '
                'a new password reset link'
            )
        except BadData:
            raise InvalidPasswordResetToken(
                'Invalid token - Request a new password reset link'
            )

        user = self.user_service.get_user(data.get('user.id'))
        if user is None:
            raise InvalidPasswordResetToken(
                'Invalid token - User not found'
            )

        last_login = data.get('user.last_login')
        if str(user.last_login) > last_login:
            raise InvalidPasswordResetToken(
                'Invalid token - User has logged in since '
                'this token was requested'
            )

        password_date = data.get('user.password_date')
        if str(user.password_date) > password_date:
            raise InvalidPasswordResetToken(
                'Invalid token - Password has already been changed '
                'since this token was requested'
            )

        return user


def database_login_factory(context, request):
    return DatabaseUserService(
        request.db,
        rate_limiters={
            'global': request.find_service(
                IRateLimiter,
                name='global.login',
                context=None
            ),
            'user': request.find_service(
                IRateLimiter,
                name='user.login',
                context=None
            )
        }
    )


def user_token_factory(context, request):
    return UserTokenService(
        request.find_service(IUserService),
        request.registry.settings
    )
