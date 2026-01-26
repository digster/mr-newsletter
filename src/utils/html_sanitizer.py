"""HTML sanitization utilities for safe email rendering."""

from typing import Optional

import bleach
import html2text
from bleach.css_sanitizer import CSSSanitizer

# Allowed HTML tags for email content
ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "address",
    "b",
    "blockquote",
    "body",
    "br",
    "center",
    "code",
    "dd",
    "del",
    "dfn",
    "div",
    "dl",
    "dt",
    "em",
    "font",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "hr",
    "html",
    "i",
    "img",
    "ins",
    "kbd",
    "li",
    "link",
    "meta",
    "ol",
    "p",
    "pre",
    "q",
    "s",
    "samp",
    "small",
    "span",
    "strike",
    "strong",
    "style",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "tt",
    "u",
    "ul",
    "var",
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    "*": ["class", "id", "style"],
    "a": ["href", "title", "target", "rel"],
    "body": ["bgcolor", "text", "link", "vlink", "alink"],
    "img": ["src", "alt", "title", "width", "height"],
    "font": ["color", "face", "size"],
    "link": ["rel", "type", "href"],
    "meta": ["charset", "name", "content", "http-equiv"],
    "table": ["border", "cellpadding", "cellspacing", "width", "bgcolor"],
    "td": ["colspan", "rowspan", "width", "align", "valign", "bgcolor"],
    "th": ["colspan", "rowspan", "width", "align", "valign", "bgcolor"],
    "tr": ["align", "valign", "bgcolor"],
    "div": ["align"],
    "p": ["align"],
}

# Allowed CSS properties in style attributes
ALLOWED_STYLES = [
    "background-color",
    "border",
    "border-color",
    "border-radius",
    "border-style",
    "border-width",
    "color",
    "display",
    "font-family",
    "font-size",
    "font-style",
    "font-weight",
    "height",
    "line-height",
    "margin",
    "margin-bottom",
    "margin-left",
    "margin-right",
    "margin-top",
    "max-width",
    "min-height",
    "min-width",
    "padding",
    "padding-bottom",
    "padding-left",
    "padding-right",
    "padding-top",
    "text-align",
    "text-decoration",
    "vertical-align",
    "width",
]


def sanitize_html(html_content: Optional[str]) -> str:
    """Sanitize HTML content for safe rendering.

    Args:
        html_content: Raw HTML content from email.

    Returns:
        Sanitized HTML content safe for rendering.
    """
    if not html_content:
        return ""

    # Configure CSS sanitizer with allowed properties
    css_sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_STYLES)

    # Clean the HTML
    cleaned = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        strip=True,
    )

    # Add target="_blank" and rel="noopener" to all links for security
    cleaned = bleach.linkify(
        cleaned,
        callbacks=[_add_link_attributes],
        skip_tags=["pre", "code"],
    )

    return cleaned


def _add_link_attributes(attrs: dict, new: bool = False) -> dict:
    """Add security attributes to links.

    Args:
        attrs: Link attributes.
        new: Whether this is a new link.

    Returns:
        Modified attributes with security additions.
    """
    attrs[(None, "target")] = "_blank"
    attrs[(None, "rel")] = "noopener noreferrer"
    return attrs


def html_to_safe_content(html_content: Optional[str]) -> str:
    """Convert HTML to sanitized content with wrapper styling.

    Args:
        html_content: Raw HTML content.

    Returns:
        Sanitized HTML wrapped in a container div.
    """
    sanitized = sanitize_html(html_content)

    # Wrap in a container with basic styling
    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: inherit;
                max-width: 100%;
                overflow-wrap: break-word;">
        {sanitized}
    </div>
    """


def sanitize_html_for_webview(html_content: Optional[str]) -> str:
    """Sanitize HTML for WebView rendering, preserving styles.

    This is a lighter sanitization that preserves <style> tags and their
    content for proper rendering in a sandboxed WebView.

    Args:
        html_content: Raw HTML content from email.

    Returns:
        Sanitized HTML suitable for WebView rendering.
    """
    if not html_content:
        return ""

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove dangerous tags (script, iframe, object, embed, form)
    dangerous_tags = ["script", "iframe", "object", "embed", "form", "input", "button"]
    for tag in soup.find_all(dangerous_tags):
        tag.decompose()

    # Remove dangerous attributes
    dangerous_attrs = ["onclick", "onload", "onerror", "onmouseover", "onfocus", "onblur"]
    for tag in soup.find_all(True):
        for attr in dangerous_attrs:
            if tag.has_attr(attr):
                del tag[attr]

    # Add security attributes to links
    for link in soup.find_all("a"):
        link["target"] = "_blank"
        link["rel"] = "noopener noreferrer"

    # Return as string with proper HTML structure
    result = str(soup)

    # Ensure we have a complete HTML document for WebView
    if "<html" not in result.lower():
        result = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 16px;
            margin: 0;
            background-color: #1e1e1e;
            color: #e0e0e0;
        }}
        a {{ color: #6db3f2; }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        /* Hide broken images gracefully */
        img[src]::before {{
            content: '';
            display: block;
        }}
    </style>
</head>
<body>
{result}
</body>
</html>"""
    else:
        # For emails with existing HTML structure, inject CSS to handle broken images
        result = result.replace(
            "</head>",
            """<style>
        img { max-width: 100%; height: auto; }
    </style>
</head>""",
            1,
        )

    return result


def html_to_plain_text(html_content: Optional[str]) -> str:
    """Convert HTML to plain text for LLM processing.

    Uses html2text to convert HTML to readable plain text while
    preserving link URLs and basic structure.

    Args:
        html_content: Raw HTML content from email.

    Returns:
        Plain text representation of the HTML content.
    """
    if not html_content:
        return ""

    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep link URLs
    h.ignore_images = True  # Skip image alt text clutter
    h.body_width = 0  # No line wrapping
    return h.handle(html_content).strip()
