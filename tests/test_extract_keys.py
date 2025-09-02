import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gui_main


def test_extract_keys_from_html():
    html = (
        "<span class='secret-placeholder'>KEY123</span>"
        "<span class='secret-placeholder'>KEY234</span>"
        "<span class='secret-placeholder'>KEY123</span>"
    )
    result = gui_main.FunPayKeyChecker.extract_keys_from_html(None, html)
    assert result == ["KEY123", "KEY234"]

