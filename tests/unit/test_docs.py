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
from armonaut.docs.services import MisakaMarkdownRenderer


@pytest.mark.parametrize('lexer', ['', 'zzz'])
def test_render_code_block_no_lexer(lexer):
    """Assert that code-blocks are rendered with <pre><code>
    when there is no Pygments lexer for that language.
    """
    renderer = MisakaMarkdownRenderer()

    rendered = renderer.render_markdown(f"""```{lexer}
    <html>This is test code</html>
    ```""")

    assert '\n<pre><code>' in rendered
    assert '</code></pre>\n' in rendered
    assert 'This is test code' in rendered
    assert '<html>' not in rendered
