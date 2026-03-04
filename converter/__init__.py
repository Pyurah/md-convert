"""Markdown to Google Docs converter package."""

from .md_to_html import convert_markdown_to_gdocs_html
from .clipboard import copy_html_to_clipboard

__all__ = ["convert_markdown_to_gdocs_html", "copy_html_to_clipboard"]
