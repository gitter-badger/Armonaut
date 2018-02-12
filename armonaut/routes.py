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


def includeme(config):
    armonaut = config.get_settings().get('armonaut.domain')

    config.add_route('index', '/')

    config.add_route('auth.authorize', '/auth/authorize', domain=armonaut)
    config.add_route('auth.callback', '/auth/callback', domain=armonaut)
    config.add_route('auth.logout', '/auth/logout', domain=armonaut)

    config.add_route(
        'auth.pusher',
        '/auth/pusher/{owner}/{name}',
        traverse='/{owner}/{name}',
        factory='armonaut.project.models:ProjectFactory',
        domain=armonaut
    )

    config.add_route(
        'builds.get_build',
        '/gh/{owner}/{name}/builds/{number}',
        traverse='/{owner}/{name}',
        factory='armonaut.project.models:ProjectFactory',
        domain=armonaut
    )
