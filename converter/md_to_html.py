"""
Markdown to Google Docs-compatible HTML converter.

Converts markdown text to HTML with inline CSS styles that Google Docs
will preserve when pasting from the clipboard.
"""

import re
import markdown2
from bs4 import BeautifulSoup, NavigableString

# ---------------------------------------------------------------------------
# Google Docs-compatible inline style definitions
# ---------------------------------------------------------------------------

STYLES = {
    "h1": "font-size:24pt;font-weight:bold;font-family:Arial,sans-serif;margin-bottom:6pt;margin-top:12pt;",
    "h2": "font-size:18pt;font-weight:bold;font-family:Arial,sans-serif;margin-bottom:4pt;margin-top:10pt;",
    "h3": "font-size:14pt;font-weight:bold;font-family:Arial,sans-serif;margin-bottom:4pt;margin-top:8pt;",
    "h4": "font-size:12pt;font-weight:bold;font-family:Arial,sans-serif;margin-bottom:4pt;margin-top:8pt;",
    "h5": "font-size:11pt;font-weight:bold;font-family:Arial,sans-serif;margin-bottom:4pt;margin-top:6pt;",
    "h6": "font-size:10pt;font-weight:bold;font-style:italic;font-family:Arial,sans-serif;margin-bottom:4pt;margin-top:6pt;",
    "p": "font-size:11pt;font-family:Arial,sans-serif;line-height:1.5;margin-bottom:6pt;",
    "li": "font-size:11pt;font-family:Arial,sans-serif;line-height:1.5;",
    "ul": "margin-left:18pt;margin-bottom:6pt;",
    "ol": "margin-left:18pt;margin-bottom:6pt;",
    "a": "color:#1155cc;text-decoration:underline;",
    "strong": "font-weight:bold;",
    "em": "font-style:italic;",
    "del": "text-decoration:line-through;",
    "code_inline": "font-family:Consolas,'Courier New',monospace;font-size:10pt;background-color:#f5f5f5;padding:1pt 3pt;",
    "code_block_cell": (
        "background-color:#f5f5f5;border:1px solid #e0e0e0;padding:8pt;"
        "font-family:Consolas,'Courier New',monospace;font-size:10pt;white-space:pre-wrap;"
    ),
    "code_block_table": "border-collapse:collapse;width:100%;margin:8pt 0;",
    "table": "border-collapse:collapse;margin:8pt 0;",
    "th": "border:1px solid #000000;padding:4pt 8pt;font-weight:bold;font-family:Arial,sans-serif;font-size:11pt;background-color:#f0f0f0;",
    "td": "border:1px solid #000000;padding:4pt 8pt;font-family:Arial,sans-serif;font-size:11pt;",
    "blockquote": (
        "margin-left:16pt;padding-left:8pt;border-left:3px solid #cccccc;"
        "color:#555555;font-style:italic;font-family:Arial,sans-serif;font-size:11pt;"
        "margin-bottom:6pt;"
    ),
    "hr": "border:none;border-bottom:1px solid #cccccc;margin:12pt 0;",
}

# markdown2 extras to enable
MD_EXTRAS = [
    "fenced-code-blocks",
    "tables",
    "task_list",
    "strike",
    "header-ids",
    "cuddled-lists",
    "break-on-newline",
    "code-friendly",
]


def convert_markdown_to_gdocs_html(markdown_text: str) -> str:
    """
    Convert markdown text to Google Docs-compatible HTML with inline styles.

    Parameters
    ----------
    markdown_text : str
        Raw markdown text.

    Returns
    -------
    str
        HTML string with inline CSS suitable for Google Docs clipboard paste.
    """
    # Step 1: Convert markdown to standard HTML
    raw_html = markdown2.markdown(markdown_text, extras=MD_EXTRAS)

    # Step 2: Parse with BeautifulSoup for DOM manipulation
    soup = BeautifulSoup(str(raw_html), "html.parser")

    # Step 3: Apply inline styles to each element type
    _style_headings(soup)
    _style_paragraphs(soup)
    _style_lists(soup)
    _style_links(soup)
    _style_inline_formatting(soup)
    _style_code_blocks(soup)
    _style_inline_code(soup)
    _style_tables(soup)
    _style_blockquotes(soup)
    _style_horizontal_rules(soup)
    _style_task_lists(soup)

    # Step 4: Wrap in a container div for consistent base styling
    wrapper = soup.new_tag(
        "div",
        style="font-family:Arial,sans-serif;font-size:11pt;",
    )
    # Move all top-level contents into wrapper
    children = list(soup.children)
    for child in children:
        wrapper.append(child.extract())
    soup.append(wrapper)

    return str(soup)


# ---------------------------------------------------------------------------
# Private helper functions for styling each element type
# ---------------------------------------------------------------------------


def _merge_style(tag, new_style: str):
    """Append inline style to an element, preserving any existing styles."""
    existing = tag.get("style", "")
    if existing and not existing.endswith(";"):
        existing += ";"
    tag["style"] = existing + new_style


def _style_headings(soup: BeautifulSoup):
    """Apply heading styles (h1-h6)."""
    for level in range(1, 7):
        tag_name = f"h{level}"
        for tag in soup.find_all(tag_name):
            _merge_style(tag, STYLES[tag_name])


def _style_paragraphs(soup: BeautifulSoup):
    """Apply paragraph styles."""
    for tag in soup.find_all("p"):
        # Skip paragraphs inside blockquotes (handled separately)
        if tag.parent and tag.parent.name == "blockquote":
            continue
        _merge_style(tag, STYLES["p"])


def _style_lists(soup: BeautifulSoup):
    """Apply list and list-item styles."""
    for tag in soup.find_all("ul"):
        _merge_style(tag, STYLES["ul"])
    for tag in soup.find_all("ol"):
        _merge_style(tag, STYLES["ol"])
    for tag in soup.find_all("li"):
        _merge_style(tag, STYLES["li"])


def _style_links(soup: BeautifulSoup):
    """Apply link styles."""
    for tag in soup.find_all("a"):
        _merge_style(tag, STYLES["a"])


def _style_inline_formatting(soup: BeautifulSoup):
    """Apply bold, italic, and strikethrough styles."""
    for tag in soup.find_all("strong"):
        _merge_style(tag, STYLES["strong"])
    for tag in soup.find_all("em"):
        _merge_style(tag, STYLES["em"])
    for tag in soup.find_all("del"):
        _merge_style(tag, STYLES["del"])


def _style_code_blocks(soup: BeautifulSoup):
    """
    Replace <pre><code> blocks with a single-cell table for reliable
    background color in Google Docs.
    """
    for pre_tag in soup.find_all("pre"):
        code_tag = pre_tag.find("code")
        if not code_tag:
            continue

        # Get the code text content
        code_text = code_tag.get_text()

        # Create a table wrapper for reliable background color
        table = soup.new_tag("table", style=STYLES["code_block_table"])
        tr = soup.new_tag("tr")
        td = soup.new_tag("td", style=STYLES["code_block_cell"])
        td.string = code_text
        tr.append(td)
        table.append(tr)

        # Replace the <pre> with the table
        pre_tag.replace_with(table)


def _style_inline_code(soup: BeautifulSoup):
    """Apply inline code styles to <code> elements not inside <pre>."""
    for tag in soup.find_all("code"):
        # Skip code blocks (already handled — those are inside tables now)
        if tag.parent and tag.parent.name in ("pre", "td"):
            continue
        _merge_style(tag, STYLES["code_inline"])


def _style_tables(soup: BeautifulSoup):
    """Apply table, th, and td styles (skip code-block tables)."""
    for tag in soup.find_all("table"):
        # Skip code block tables (they already have code_block_table style)
        if STYLES["code_block_table"] in tag.get("style", ""):
            continue
        _merge_style(tag, STYLES["table"])

    for tag in soup.find_all("th"):
        _merge_style(tag, STYLES["th"])

    for tag in soup.find_all("td"):
        # Skip code block cells
        if STYLES["code_block_cell"] in tag.get("style", ""):
            continue
        _merge_style(tag, STYLES["td"])


def _style_blockquotes(soup: BeautifulSoup):
    """
    Convert <blockquote> to styled <div> elements since Google Docs
    doesn't have a native blockquote style.
    """
    for tag in soup.find_all("blockquote"):
        # Create a replacement div
        div = soup.new_tag("div", style=STYLES["blockquote"])

        # Move children from blockquote to div
        for child in list(tag.children):
            if isinstance(child, NavigableString):
                div.append(child.extract())
            else:
                # Strip paragraph wrapper inside blockquotes for cleaner output
                if child.name == "p":
                    for inner in list(child.children):
                        div.append(inner.extract())
                else:
                    div.append(child.extract())

        tag.replace_with(div)


def _style_horizontal_rules(soup: BeautifulSoup):
    """Replace <hr> with a styled div since Google Docs ignores <hr>."""
    for tag in soup.find_all("hr"):
        div = soup.new_tag("div", style=STYLES["hr"])
        div.string = "\u00a0"  # non-breaking space to give it height
        tag.replace_with(div)


def _style_task_lists(soup: BeautifulSoup):
    """
    Style task list items generated by markdown2's task_list extra.
    markdown2 generates <li> with class 'task-list-item' and an <input> checkbox.
    We replace the checkbox with a unicode character for Google Docs compatibility.
    """
    for li in soup.find_all("li", class_="task-list-item"):
        checkbox = li.find("input", attrs={"type": "checkbox"})
        if checkbox:
            checked = checkbox.has_attr("checked")
            symbol = "☑ " if checked else "☐ "
            checkbox.replace_with(symbol)
