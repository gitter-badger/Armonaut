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

import os
import typing
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
csrf = CSRFProtect()
limit = Limiter()
login = LoginManager()


class Model(db.Model):
    __abstract__ = True

    id = sqlalchemy.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sqlalchemy.text('gen_random_uuid()')
    )


def create_app(config: typing.Optional[str]=None) -> Flask:
    app = Flask(__name__)

    if config is None:
        config = os.environ['APP_SETTINGS']
    app.config.from_object(config)

    db.init_app(app)
    csrf.init_app(app)
    login.init_app(app)
    limit.init_app(app)

    register_blueprints(app)

    return app


def register_blueprints(app: Flask):
    from armonaut.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
