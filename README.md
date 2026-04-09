# Markdown to Google Docs Converter

A local web application that converts Markdown text into Google Docs-compatible rich HTML and copies it to your clipboard for seamless pasting.

## Features

- **Live Preview** — See your formatted Markdown rendered in real-time as you type
- **Rich Clipboard Copy** — Copies HTML as CF_HTML format so Google Docs preserves all formatting
- **Google Docs Optimized** — Inline CSS styling tuned for Google Docs compatibility:
  - Headings (H1–H6) with proper font sizes
  - Bold, italic, strikethrough
  - Ordered and unordered lists
  - Tables with borders
  - Code blocks with monospace font and background
  - Blockquotes with left border
  - Links (clickable in Google Docs)
  - Task lists with checkbox characters
- **File Upload** — Load `.md` files directly into the editor
- **HTML Source View** — Toggle to see the raw HTML being generated
- **Keyboard Shortcuts** — `Ctrl+Shift+C` to copy to clipboard
- **Dark Theme Editor** — Hytale-docs-inspired UI with dark navy header, teal accents, and clean white preview
- **No-Terminal Launch** — Double-click `Start MD Converter.vbs` to launch without opening a console window
- **In-Browser Shutdown** — Stop the server directly from the UI with the ⏹ Stop button

## Requirements

- **Python 3.9+**
- **Windows** (for clipboard CF_HTML support via pywin32)

## Setup

1. **Navigate to the project directory:**

   ```bash
   cd "MD Conversion"
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

5. **Open your browser** to [http://localhost:5000](http://localhost:5000) (opens automatically).

### Quick Start (No Terminal)

After initial setup, just **double-click `Start MD Converter.vbs`** in the project folder. It launches the server in the background (no console window) and opens your browser automatically.

## Usage

1. **Type or paste Markdown** in the left editor pane
2. **Preview** appears in real-time on the right pane
3. Click **"📋 Copy to Clipboard"** (or press `Ctrl+Shift+C`)
4. Switch to **Google Docs** and press `Ctrl+V` to paste with formatting

### Shutting Down

- **From the UI**: Click the **⏹ Stop** button in the top-right corner of the toolbar
- **From the terminal**: Press `Ctrl+C` in the terminal running the server

## Project Structure

```
MD Conversion/
├── app.py                    # Flask application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── Start MD Converter.vbs    # Double-click launcher (no console)
├── converter/
│   ├── __init__.py           # Package exports
│   ├── md_to_html.py         # Markdown → Google Docs HTML converter
│   └── clipboard.py          # Windows CF_HTML clipboard handler
├── templates/
│   └── index.html            # Web UI template (Hytale-inspired theme)
├── static/
│   ├── css/
│   │   └── style.css         # Hytale-docs-inspired dark/light theme
│   └── js/
│       └── app.js            # Frontend JavaScript (preview, clipboard, shutdown)
├── .vscode/
│   └── launch.json           # VS Code debug configuration
└── plans/
    └── plan.md               # Architecture plan
```

## How It Works

### Conversion Pipeline

1. **Markdown → HTML**: Uses `markdown2` with GFM extras (tables, fenced code blocks, task lists, strikethrough)
2. **HTML → Styled HTML**: BeautifulSoup walks the DOM and injects inline CSS on every element (because Google Docs ignores `<style>` tags and CSS classes)
3. **Styled HTML → Clipboard**: Uses Windows `win32clipboard` to set CF_HTML format, which Google Docs reads as rich text when pasting

### Why Inline CSS?

Google Docs clipboard paste only respects **inline `style=""` attributes**. It strips:
- `<style>` blocks
- CSS class references
- External stylesheets

So every `<h1>`, `<p>`, `<td>`, etc. gets its own `style` attribute with Google Docs-compatible properties.

### Code Block Trick

Google Docs often strips `background-color` from regular elements but preserves it on **table cells**. So code blocks (`<pre><code>`) are wrapped in a single-cell `<table>` for reliable background color rendering.

## Supported Markdown Features

| Feature | Markdown Syntax | Google Docs Result |
|---------|----------------|-------------------|
| Headings | `# H1` through `###### H6` | Proper heading sizes |
| Bold | `**text**` | Bold text |
| Italic | `*text*` | Italic text |
| Strikethrough | `~~text~~` | Strikethrough text |
| Links | `[text](url)` | Clickable link |
| Unordered Lists | `- item` | Bulleted list |
| Ordered Lists | `1. item` | Numbered list |
| Task Lists | `- [x] done` / `- [ ] todo` | ☑/☐ checkboxes |
| Tables | Pipe tables | Bordered table |
| Code (inline) | `` `code` `` | Monospace text |
| Code Blocks | ```` ``` ```` | Monospace block with background |
| Blockquotes | `> quote` | Indented with left border |
| Horizontal Rule | `---` | Horizontal line |

## Future Enhancements

- Google Docs API integration (create documents directly)
- Custom font/size preferences
- Export to DOCX/PDF
- Markdown syntax toolbar
- Multiple theme presets
