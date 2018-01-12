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

import misaka
import houdini
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name
from zope.interface import implementer
from armonaut.docs.interfaces import MarkdownRenderer


class HtmlRenderer(misaka.HtmlRenderer):
    def blockcode(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = None

        # If we find a language lexer we highlight for that lexer
        if lexer:
            formatter = HtmlFormatter()
            return highlight(text, lexer, formatter)

        # Default case we escape the HTML and render as <pre><code>
        return f'\n<pre><code>{houdini.escape_html(text.strip())}</code></pre>\n'


@implementer(MarkdownRenderer)
class MisakaMarkdownRenderer:
    def __init__(self):
        self.renderer = misaka.Markdown(
            HtmlRenderer(),
            extensions=('fenced-code',
                        'strikethrough')
        )

    def render_markdown(self, data):
        return self.renderer(data)
