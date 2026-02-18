"""
Utility helpers for path conversion and sanitization.
"""

import os
import re


def sanitize_path(path: str) -> str:
    """
    Sanitize each path component by replacing unsafe characters with "_".

    Dots are preserved to keep host-like directory names (e.g. docs.example.com).
    If the path is empty after sanitization, return a safe markdown filename.
    """
    path_parts = path.split(os.sep)

    sanitized_parts = []
    for part in path_parts:
        if part:
            sanitized_part = re.sub(r"[^a-zA-Z0-9._-]", "_", part)
            sanitized_parts.append(sanitized_part)

    if not sanitized_parts:
        return "file.md"

    return os.path.join(*sanitized_parts)


def html_to_md_path(html_path: str) -> str:
    """Convert an HTML path to its markdown path."""
    if html_path.endswith(".html"):
        return html_path[:-5] + ".md"
    return html_path + ".md"
