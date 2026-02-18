import os

from site2skill.utils import html_to_md_path, sanitize_path


def test_html_to_md_path_converts_html_extension():
    assert html_to_md_path("example.com/index.html") == "example.com/index.md"
    assert html_to_md_path("example.com/guide") == "example.com/guide.md"


def test_sanitize_path_replaces_unsafe_chars():
    path = "docs@example.com/api#v1/index.md"
    expected = os.path.join("docs_example.com", "api_v1", "index.md")
    assert sanitize_path(path) == expected


def test_sanitize_path_empty_input_returns_safe_default():
    assert sanitize_path("") == "file.md"
