# Armonaut

[![Travis](https://img.shields.io/travis/SethMichaelLarson/Armonaut/master.svg)](https://travis-ci.org/SethMichaelLarson/Armonaut)
[![Codecov](https://img.shields.io/codecov/c/github/SethMichaelLarson/Armonaut/master.svg)](https://codecov.io/gh/SethMichaelLarson/Armonaut)
[![Slack](https://img.shields.io/badge/slack-%23dev-brightgreen.svg)](https://armonaut.slack.com)

Simple, Flexible, and Scalable Continuous Integration

## Features

- 20+ Popular Languages
- Customizable Machine Images
- Hundreds of Services and Tools
- Limitless Parallelization and Scalability
- Configurable executor resources
- Integrates with GitHub, Slack, and Gitter
- Tools for running and debugging builds locally with Vagrant

## Contributing

Armonaut has a guide to start contributing found in [`CONTRIBUTING.md`](https://github.com/SethMichaelLarson/Armonaut/blob/master/CONTRIBUTING.md)
and additionally has a Code of Conduct found in [`CODE_OF_CONDUCT.md`](https://github.com/SethMichaelLarson/Armonaut/blob/master/CODE_OF_CONDUCT.md)
Please read and follow the Code of Conduct any time you're interacting with or participating in the Armonaut Open Source community.

## Releases

Armonaut follows [Semantic Versioning](http://semver.org/spec/v2.0.0.html)
with major versions meaning breaking changes,
minor versions meaning additional functionality or changes to beta functionality
and patch versions meaning bug fixes to existing functionality.

Whenever a change is made to the functionality of Armonaut an entry is added to
[`CHANGELOG.md`](https://github.com/SethMichaelLarson/Armonaut/blob/master/CHANGELOG.md).
View the latest releases and changes within the same file.

## Open Source

Armonaut would not be possible without the following Open Source projects:

The template for the Armonaut web application is based heavily on [Warehouse](https://github.com/pypa/warehouse)
which is [licensed under Apache-2.0](https://github.com/pypa/warehouse/blob/master/LICENSE). 

[alembic](https://bitbucket.org/zzzeek/alembic) (MIT),
[argon2-cffi](https://github.com/hynek/argon2_cffi) (MIT),
[boto3](https://boto3.readthedocs.io/en/latest/) (Apache-2.0),
[celery](http://celeryproject.org/) (BSD),
[celery-redbeat](https://github.com/sibson/redbeat) (Apache-2.0),
[click](http://github.com/mitsuhiko/click) (BSD),
[codecov](http://github.com/codecov/codecov-python) (Apache-2.0),
[coverage](https://bitbucket.org/ned/coveragepy) (Apache-2.0),
[dsnparse](http://github.com/Jaymon/dsnparse) (MIT),
[factory-boy](http://factoryboy.readthedocs.io/en/latest/) (MIT),
[first](https://github.com/hynek/first/) (MIT),
[flake8](https://gitlab.com/pycqa/flake8) (MIT),
[Gulp](https://github.com/gulpjs/gulp) (MIT),
[gunicorn](http://gunicorn.org/) (MIT),
[houdini.py](http://python-houdini.61924.nl/) (MIT),
[itsdangerous](http://github.com/mitsuhiko/itsdangerous) (BSD),
[jQuery](https://jquery.org) (MIT)
[limits](https://limits.readthedocs.org/) (MIT),
[misaka](https://github.com/FSX/misaka) (MIT),
[msgpack-python](http://msgpack.org/) (Apache-2.0),
[passlib](https://bitbucket.org/ecollins/passlib) (BSD),
[pretend](https://github.com/alex/pretend) (BSD),
[psycopg2](http://initd.org/psycopg/) (LGPL),
[pusher](https://pusher.com) (MIT),
[pygments](http://pygments.org/) (BSD),
[pyramid](https://trypyramid.com/) (ZPL),
[pyramid-debugtoolbar](https://docs.pylonsproject.org/projects/pyramid-debugtoolbar/en/latest/) (BSD-like),
[pyramid-jinja2](https://github.com/Pylons/pyramid_jinja2) (BSD-like),
[pyramid-mailer](http://docs.pylonsproject.org/projects/pyramid-mailer/en/latest/) (BSD),
[pyramid-multiauth](https://github.com/mozilla-services/pyramid_multiauth) (MPL-2.0),
[pyramid-retry](https://github.com/Pylons/pyramid_retry) (MIT),
[pyramid-services](https://github.com/mmerickel/pyramid_services) (MIT),
[pyramid-tm](http://docs.pylonsproject.org/projects/pyramid-tm/en/latest/) (BSD-like),
[pytest](http://pytest.org/) (MIT),
[pytest-cov](https://github.com/pytest-dev/pytest-cov) (MIT),
[pytest-needle](https://github.com/jlane9/pytest-needle) (MIT),
[pytest-postgresql](https://github.com/ClearcodeHQ/pytest-postgresql) (LGPL),
[raven](https://github.com/getsentry/raven-python) (BSD),
[redis-py](http://github.com/andymccurdy/redis-py) (MIT),
[sqlalchemy](http://sqlalchemy.org/) (MIT),
[structlog](http://www.structlog.org/) (Apache-2.0),
[webob](http://webob.org/) (MIT),
[webtest](http://webtest.pythonpaste.org/) (MIT),
[whitenoise](http://whitenoise.evans.io/) (MIT),
[wtforms](http://wtforms.simplecodes.com/) (BSD),
[zope.interface](https://github.com/zopefoundation/zope.interface) (ZPL), and
[zope.sqlalchemy](http://pypi.python.org/pypi/zope.sqlalchemy) (ZPL)

## License

Armonaut is licensed under the Apache-2.0 license. See
[`LICENSE`](https://github.com/SethMichaelLarson/Armonaut/blob/master/LICENSE)
for more information.

```
Copyright 2018 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
