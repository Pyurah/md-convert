# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
python app.py

# Install dependencies (Windows, requires venv first)
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
```

There are no tests and no linter configured.

## Architecture

Single-file Flask app (`app.py`) serving a local web UI on `localhost:5000`. The conversion pipeline lives entirely in the `converter/` package.

**Conversion pipeline** (`/api/convert`, `/api/clipboard`):
1. `markdown2.markdown()` parses Markdown with GFM extras (tables, fenced code, task lists, strikethrough)
2. BeautifulSoup walks the resulting DOM and injects inline `style=""` attributes on every element — this is required because Google Docs strips `<style>` blocks and CSS classes on paste
3. Code blocks (`<pre><code>`) are replaced with a single-cell `<table>` because Google Docs preserves `background-color` on table cells but strips it from other elements
4. Blockquotes (`<blockquote>`) and horizontal rules (`<hr>`) are replaced with `<div>` elements since Google Docs has no native equivalents
5. Task list checkboxes (`<input type="checkbox">`) are replaced with `☑`/`☐` unicode characters
6. `clipboard.py` wraps the final HTML in the Windows `CF_HTML` clipboard format (with byte-offset header) using `win32clipboard`, then sets it alongside a plain-text fallback

**Windows-only**: The clipboard functionality requires `pywin32`. The app is designed for Windows only.

**Frontend** (`static/js/app.js`): Handles live preview (calls `/api/convert` on input), clipboard copy (calls `/api/clipboard`), file upload, HTML source view toggle, and the `Ctrl+Shift+C` keyboard shortcut.

**Shutdown**: The `/api/shutdown` endpoint sends `SIGTERM` to itself after a 0.5s delay, allowing the response to be returned before the process exits. `Start MD Converter.vbs` launches the server without a console window.
