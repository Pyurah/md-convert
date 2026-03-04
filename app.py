"""
Markdown to Google Docs Converter - Flask Application

A local web application that converts Markdown to Google Docs-compatible
rich HTML and copies it to the clipboard for pasting.

Usage:
    python app.py

Then open http://localhost:5000 in your browser.
"""

import os
import signal
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify

from converter.md_to_html import convert_markdown_to_gdocs_html
from converter.clipboard import copy_html_to_clipboard

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/api/convert", methods=["POST"])
def api_convert():
    """
    Convert markdown to Google Docs-compatible HTML.

    Request JSON:
        { "markdown": "# Hello World" }

    Response JSON:
        { "html": "<div style='...'>...</div>" }
    """
    data = request.get_json()
    if not data or "markdown" not in data:
        return jsonify({"error": "Missing 'markdown' field in request"}), 400

    markdown_text = data["markdown"]
    html_output = convert_markdown_to_gdocs_html(markdown_text)

    return jsonify({"html": html_output})


@app.route("/api/clipboard", methods=["POST"])
def api_clipboard():
    """
    Convert markdown to HTML and copy to clipboard as rich text.

    Request JSON:
        { "markdown": "# Hello World" }

    Response JSON:
        { "success": true, "message": "Rich HTML copied to clipboard!" }
    """
    data = request.get_json()
    if not data or "markdown" not in data:
        return jsonify({"error": "Missing 'markdown' field in request"}), 400

    markdown_text = data["markdown"]
    html_output = convert_markdown_to_gdocs_html(markdown_text)
    result = copy_html_to_clipboard(html_output)

    return jsonify(result)


@app.route("/api/shutdown", methods=["POST"])
def api_shutdown():
    """
    Shut down the Flask server gracefully.
    Called from the UI's "Stop Server" button.
    """
    def shutdown():
        # Give time for the response to be sent
        import time
        time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=shutdown, daemon=True).start()
    return jsonify({"success": True, "message": "Server shutting down..."})


def open_browser():
    """Open the default browser to the app URL after a short delay."""
    webbrowser.open("http://localhost:5000")


if __name__ == "__main__":
    # Open browser automatically after server starts
    threading.Timer(1.5, open_browser).start()

    print("=" * 60)
    print("  Markdown to Google Docs Converter")
    print("  Open http://localhost:5000 in your browser")
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)

    app.run(host="localhost", port=5000, debug=False)
