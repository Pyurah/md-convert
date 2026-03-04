"""
Windows clipboard handler for CF_HTML format.

Copies HTML content to the Windows clipboard in CF_HTML format so that
Google Docs (and other rich text applications) can paste it with formatting.
"""

import html


def _build_cf_html(html_content: str) -> bytes:
    """
    Build a CF_HTML clipboard payload from an HTML fragment.

    The CF_HTML format requires a specific header with byte offsets:
        Version:0.9
        StartHTML:XXXXXXXX
        EndHTML:XXXXXXXX
        StartFragment:XXXXXXXX
        EndFragment:XXXXXXXX

    Parameters
    ----------
    html_content : str
        The HTML fragment to place on the clipboard.

    Returns
    -------
    bytes
        The complete CF_HTML payload encoded as UTF-8.
    """
    # Template with placeholders for the byte offsets
    # We use 10-digit zero-padded numbers for the offsets
    header_template = (
        "Version:0.9\r\n"
        "StartHTML:{start_html:010d}\r\n"
        "EndHTML:{end_html:010d}\r\n"
        "StartFragment:{start_fragment:010d}\r\n"
        "EndFragment:{end_fragment:010d}\r\n"
    )

    # Pre-fragment and post-fragment HTML wrappers
    pre_fragment = "<html>\r\n<body>\r\n<!--StartFragment-->"
    post_fragment = "<!--EndFragment-->\r\n</body>\r\n</html>"

    # Calculate a dummy header first to know its length
    dummy_header = header_template.format(
        start_html=0, end_html=0, start_fragment=0, end_fragment=0
    )
    header_length = len(dummy_header.encode("utf-8"))

    # Calculate all byte offsets
    start_html = header_length
    start_fragment = start_html + len(pre_fragment.encode("utf-8"))
    end_fragment = start_fragment + len(html_content.encode("utf-8"))
    end_html = end_fragment + len(post_fragment.encode("utf-8"))

    # Build the final header with correct offsets
    final_header = header_template.format(
        start_html=start_html,
        end_html=end_html,
        start_fragment=start_fragment,
        end_fragment=end_fragment,
    )

    # Assemble the complete payload
    payload = final_header + pre_fragment + html_content + post_fragment
    return payload.encode("utf-8")


def copy_html_to_clipboard(html_content: str) -> dict:
    """
    Copy HTML content to the Windows clipboard in CF_HTML format.

    Also sets CF_UNICODETEXT as a plain-text fallback (strips HTML tags).

    Parameters
    ----------
    html_content : str
        The HTML content to copy.

    Returns
    -------
    dict
        A dictionary with 'success' (bool) and 'message' (str).
    """
    try:
        import win32clipboard  # type: ignore

        # Build the CF_HTML payload
        cf_html_data = _build_cf_html(html_content)

        # Register the CF_HTML format
        cf_html_format = win32clipboard.RegisterClipboardFormat("HTML Format")

        # Create a plain-text fallback by stripping tags
        from bs4 import BeautifulSoup

        plain_text = BeautifulSoup(html_content, "html.parser").get_text()

        # Open clipboard and set data
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(cf_html_format, cf_html_data)
            win32clipboard.SetClipboardData(
                win32clipboard.CF_UNICODETEXT, plain_text
            )
        finally:
            win32clipboard.CloseClipboard()

        return {"success": True, "message": "Rich HTML copied to clipboard!"}

    except ImportError:
        return {
            "success": False,
            "message": (
                "pywin32 is not installed. Install it with: "
                "pip install pywin32"
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to copy to clipboard: {str(e)}",
        }
