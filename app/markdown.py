import mistune
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        lang = (info or "").strip().split()[0] if info else ""
        if lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
                return highlight(code, lexer, HtmlFormatter())
            except ClassNotFound:
                pass
        escaped = mistune.util.escape(code)
        return f"<pre><code>{escaped}</code></pre>"


_markdown = mistune.create_markdown(
    renderer=HighlightRenderer(escape=False),
    plugins=["strikethrough", "table", "footnotes"],
)


def render_markdown(text):
    return _markdown(text)
