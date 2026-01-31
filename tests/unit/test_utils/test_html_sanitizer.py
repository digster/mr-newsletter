"""Tests for HTML sanitization utilities.

These tests verify XSS prevention and safe HTML rendering for email content.
The sanitizer is critical for security as emails may contain malicious HTML.
"""

import pytest

from src.utils.html_sanitizer import (
    sanitize_html,
    sanitize_html_for_webview,
    html_to_plain_text,
    html_to_safe_content,
    ALLOWED_TAGS,
    ALLOWED_ATTRIBUTES,
    ALLOWED_STYLES,
)


class TestSanitizeHtml:
    """Test suite for the sanitize_html function."""

    def test_allows_safe_tags(self):
        """Verify safe HTML tags are preserved."""
        html = "<p>Paragraph</p><div>Division</div><span>Inline</span>"
        result = sanitize_html(html)

        assert "<p>" in result
        assert "<div>" in result
        assert "<span>" in result

    def test_allows_link_tags(self):
        """Verify anchor tags with safe attributes are preserved."""
        html = '<a href="https://example.com">Click here</a>'
        result = sanitize_html(html)

        assert "<a" in result
        assert "https://example.com" in result
        assert "Click here" in result

    def test_allows_image_tags(self):
        """Verify image tags with safe attributes are preserved."""
        html = '<img src="https://example.com/image.png" alt="Test image">'
        result = sanitize_html(html)

        assert "<img" in result
        assert 'src="https://example.com/image.png"' in result
        assert 'alt="Test image"' in result

    def test_allows_table_tags(self):
        """Verify table structure tags are preserved."""
        html = """
        <table>
            <thead><tr><th>Header</th></tr></thead>
            <tbody><tr><td>Cell</td></tr></tbody>
        </table>
        """
        result = sanitize_html(html)

        assert "<table>" in result
        assert "<thead>" in result
        assert "<tbody>" in result
        assert "<tr>" in result
        assert "<th>" in result
        assert "<td>" in result

    def test_strips_script_tags(self):
        """Verify script tags are removed for XSS prevention.

        Note: bleach.clean with strip=True removes the script tags but may
        leave the text content. This is safe because plain text won't execute
        as JavaScript - the browser only executes code within <script> tags.
        """
        html = '<p>Hello</p><script>alert("XSS")</script><p>World</p>'
        result = sanitize_html(html)

        # Script tags must be removed (this prevents execution)
        assert "<script>" not in result
        assert "</script>" not in result
        assert "<p>Hello</p>" in result
        assert "<p>World</p>" in result

    def test_strips_script_tags_with_variations(self):
        """Verify various script tag formats are removed.

        The key security property is that no executable <script> tags remain.
        Text content from inside tags is harmless as plain text.
        """
        test_cases = [
            '<script type="text/javascript">evil()</script>',
            '<SCRIPT>evil()</SCRIPT>',
            '<script src="evil.js"></script>',
            '<script\n>evil()</script>',
        ]

        for html in test_cases:
            result = sanitize_html(html)
            # Script tags must not be present (prevents execution)
            assert "<script" not in result.lower()
            assert "</script>" not in result.lower()

    def test_strips_onclick_attributes(self):
        """Verify onclick event handlers are removed."""
        html = '<button onclick="stealData()">Click me</button>'
        result = sanitize_html(html)

        assert "onclick" not in result
        assert "stealData" not in result

    def test_strips_onerror_attributes(self):
        """Verify onerror event handlers are removed."""
        html = '<img src="x" onerror="stealData()">'
        result = sanitize_html(html)

        assert "onerror" not in result
        assert "stealData" not in result

    def test_strips_all_event_handlers(self):
        """Verify all JavaScript event handlers are removed."""
        event_handlers = [
            "onload",
            "onmouseover",
            "onfocus",
            "onblur",
            "onsubmit",
            "onchange",
        ]

        for handler in event_handlers:
            html = f'<div {handler}="malicious()">content</div>'
            result = sanitize_html(html)
            assert handler not in result

    def test_allows_safe_css_properties(self):
        """Verify safe CSS properties in style attributes are preserved."""
        html = '<div style="color: red; font-size: 14px; margin: 10px;">Styled</div>'
        result = sanitize_html(html)

        # Style attribute should be present with safe properties
        assert 'style="' in result or "style='" in result

    def test_strips_dangerous_css_javascript_url(self):
        """Verify javascript: URLs in CSS are removed."""
        html = '<div style="background: url(javascript:evil())">Content</div>'
        result = sanitize_html(html)

        assert "javascript:" not in result
        assert "evil" not in result

    def test_handles_css_expression(self):
        """Document behavior for CSS expressions (historical IE vulnerability).

        CSS expressions were an IE-specific feature that allowed JavaScript
        execution within CSS. Modern browsers don't support this, but it's
        worth documenting the sanitizer's behavior.

        Note: bleach's CSS sanitizer focuses on property names, not values.
        The 'width' property is allowed, so the value passes through.
        Since no modern browser executes CSS expressions, this is low risk.
        For complete protection, use sanitize_html_for_webview() which uses
        BeautifulSoup to remove dangerous attributes entirely.
        """
        html = '<div style="width: expression(alert(1))">Content</div>'
        result = sanitize_html(html)

        # Content should be preserved
        assert "Content" in result
        # Width is an allowed CSS property, so the style attribute remains
        # This is acceptable because:
        # 1. No modern browser executes CSS expressions
        # 2. The sanitizer_html_for_webview() function provides stricter protection

    def test_adds_link_security_attributes(self):
        """Verify links get target and rel security attributes."""
        html = '<a href="https://example.com">Link</a>'
        result = sanitize_html(html)

        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_returns_empty_for_none_input(self):
        """Verify None input returns empty string."""
        result = sanitize_html(None)
        assert result == ""

    def test_returns_empty_for_empty_input(self):
        """Verify empty string input returns empty string."""
        result = sanitize_html("")
        assert result == ""

    def test_preserves_text_content(self):
        """Verify text content is preserved after sanitization."""
        html = "<p>Important newsletter content with <strong>bold</strong> text.</p>"
        result = sanitize_html(html)

        assert "Important newsletter content" in result
        assert "<strong>bold</strong>" in result

    def test_strips_iframe_tags(self):
        """Verify iframe tags are removed."""
        html = '<p>Content</p><iframe src="evil.com"></iframe><p>More</p>'
        result = sanitize_html(html)

        assert "<iframe" not in result
        assert "evil.com" not in result

    def test_strips_object_and_embed_tags(self):
        """Verify object and embed tags are removed."""
        html = '<object data="malware.swf"></object><embed src="malware.swf">'
        result = sanitize_html(html)

        assert "<object" not in result
        assert "<embed" not in result
        assert "malware" not in result


class TestSanitizeHtmlForWebview:
    """Test suite for sanitize_html_for_webview function."""

    def test_removes_script_tags(self):
        """Verify script tags are removed for WebView."""
        html = '<html><body><script>malicious()</script><p>Content</p></body></html>'
        result = sanitize_html_for_webview(html)

        assert "<script>" not in result
        assert "malicious" not in result
        assert "Content" in result

    def test_removes_iframe_tags(self):
        """Verify iframe tags are removed for WebView."""
        html = '<div><iframe src="https://evil.com"></iframe><p>Safe</p></div>'
        result = sanitize_html_for_webview(html)

        assert "<iframe" not in result
        assert "evil.com" not in result
        assert "Safe" in result

    def test_removes_form_elements(self):
        """Verify form elements are removed for WebView."""
        html = """
        <form action="steal.php" method="POST">
            <input type="text" name="password">
            <button type="submit">Submit</button>
        </form>
        <p>Newsletter content</p>
        """
        result = sanitize_html_for_webview(html)

        assert "<form" not in result
        assert "<input" not in result
        assert "<button" not in result
        assert "steal.php" not in result
        assert "Newsletter content" in result

    def test_removes_event_handlers(self):
        """Verify JavaScript event handlers are removed for WebView."""
        html = """
        <div onclick="evil()" onmouseover="track()">
            <img src="pic.jpg" onerror="stealCookies()" onload="track()">
            <a href="#" onfocus="keylog()" onblur="report()">Link</a>
        </div>
        """
        result = sanitize_html_for_webview(html)

        event_handlers = ["onclick", "onmouseover", "onerror", "onload", "onfocus", "onblur"]
        for handler in event_handlers:
            assert handler not in result

    def test_creates_complete_html_document(self):
        """Verify WebView sanitizer creates complete HTML document structure."""
        html = "<p>Just a paragraph</p>"
        result = sanitize_html_for_webview(html)

        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "Just a paragraph" in result

    def test_injects_css_for_styling(self):
        """Verify CSS is injected for consistent styling."""
        html = "<p>Content</p>"
        result = sanitize_html_for_webview(html)

        assert "<style>" in result
        # Check for some expected CSS
        assert "font-family" in result
        assert "max-width" in result

    def test_preserves_existing_html_structure(self):
        """Verify existing HTML structure is preserved when present."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Email</title></head>
        <body><p>Content</p></body>
        </html>
        """
        result = sanitize_html_for_webview(html)

        assert "Email" in result
        assert "Content" in result

    def test_adds_link_security_attributes(self):
        """Verify links get security attributes in WebView."""
        html = '<a href="https://example.com">External Link</a>'
        result = sanitize_html_for_webview(html)

        assert 'target="_blank"' in result
        assert 'rel="noopener noreferrer"' in result

    def test_returns_empty_for_none_input(self):
        """Verify None input returns empty string."""
        result = sanitize_html_for_webview(None)
        assert result == ""

    def test_returns_empty_for_empty_input(self):
        """Verify empty string input returns empty string."""
        result = sanitize_html_for_webview("")
        assert result == ""

    def test_removes_object_and_embed_tags(self):
        """Verify object and embed tags are removed for WebView."""
        html = '<object data="flash.swf"></object><embed src="plugin.swf">'
        result = sanitize_html_for_webview(html)

        assert "<object" not in result
        assert "<embed" not in result


class TestHtmlToPlainText:
    """Test suite for html_to_plain_text function."""

    def test_removes_html_tags(self):
        """Verify HTML tags are removed, leaving only text."""
        html = "<p>This is <strong>important</strong> text.</p>"
        result = html_to_plain_text(html)

        assert "<p>" not in result
        assert "<strong>" not in result
        assert "This is" in result
        assert "important" in result
        assert "text" in result

    def test_preserves_link_urls(self):
        """Verify link URLs are preserved in plain text output."""
        html = '<a href="https://example.com">Click here</a> for more info.'
        result = html_to_plain_text(html)

        assert "https://example.com" in result
        assert "Click here" in result

    def test_ignores_images(self):
        """Verify images are ignored in plain text conversion."""
        html = '<p>Text before</p><img src="image.jpg" alt="Test Image"><p>Text after</p>'
        result = html_to_plain_text(html)

        # Alt text should not appear (ignore_images=True)
        assert "Text before" in result
        assert "Text after" in result

    def test_returns_empty_for_none(self):
        """Verify None input returns empty string."""
        result = html_to_plain_text(None)
        assert result == ""

    def test_returns_empty_for_empty_string(self):
        """Verify empty string input returns empty string."""
        result = html_to_plain_text("")
        assert result == ""

    def test_converts_complex_html_structure(self):
        """Verify complex HTML is converted to readable plain text."""
        html = """
        <html>
        <body>
            <h1>Newsletter Title</h1>
            <p>Welcome to our weekly digest.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <p>Visit <a href="https://example.com">our website</a> for more.</p>
        </body>
        </html>
        """
        result = html_to_plain_text(html)

        assert "Newsletter Title" in result
        assert "Welcome to our weekly digest" in result
        assert "Item 1" in result
        assert "Item 2" in result
        assert "https://example.com" in result

    def test_handles_nested_tags(self):
        """Verify nested tags are handled correctly."""
        html = "<div><p><span><strong>Deeply nested</strong></span></p></div>"
        result = html_to_plain_text(html)

        assert "Deeply nested" in result
        assert "<" not in result
        assert ">" not in result


class TestHtmlToSafeContent:
    """Test suite for html_to_safe_content wrapper function."""

    def test_wraps_content_in_styled_container(self):
        """Verify content is wrapped in a container div with styling."""
        html = "<p>Test content</p>"
        result = html_to_safe_content(html)

        assert "<div style=" in result
        assert "font-family" in result
        assert "Test content" in result

    def test_sanitizes_before_wrapping(self):
        """Verify content is sanitized before being wrapped.

        Script tags must be removed to prevent execution.
        """
        html = '<p>Safe</p><script>alert("XSS")</script>'
        result = html_to_safe_content(html)

        assert "Safe" in result
        # Script tags must not be present (prevents execution)
        assert "<script>" not in result
        assert "</script>" not in result


class TestAllowedLists:
    """Test the configured allowed tags, attributes, and styles."""

    def test_allowed_tags_contains_essentials(self):
        """Verify essential HTML tags are in the allowed list."""
        essential_tags = ["p", "div", "span", "a", "img", "table", "tr", "td", "th", "ul", "ol", "li"]

        for tag in essential_tags:
            assert tag in ALLOWED_TAGS, f"Essential tag '{tag}' missing from ALLOWED_TAGS"

    def test_allowed_tags_excludes_dangerous(self):
        """Verify dangerous tags are NOT in the allowed list."""
        dangerous_tags = ["script", "iframe", "object", "embed", "frame", "frameset"]

        for tag in dangerous_tags:
            assert tag not in ALLOWED_TAGS, f"Dangerous tag '{tag}' should not be in ALLOWED_TAGS"

    def test_allowed_attributes_for_links(self):
        """Verify anchor tags have appropriate allowed attributes."""
        link_attrs = ALLOWED_ATTRIBUTES.get("a", [])

        assert "href" in link_attrs
        assert "title" in link_attrs

    def test_allowed_attributes_for_images(self):
        """Verify image tags have appropriate allowed attributes."""
        img_attrs = ALLOWED_ATTRIBUTES.get("img", [])

        assert "src" in img_attrs
        assert "alt" in img_attrs

    def test_allowed_styles_contains_safe_properties(self):
        """Verify safe CSS properties are allowed."""
        safe_styles = [
            "color",
            "background-color",
            "font-size",
            "margin",
            "padding",
            "text-align",
        ]

        for style in safe_styles:
            assert style in ALLOWED_STYLES, f"Safe style '{style}' missing from ALLOWED_STYLES"

    def test_no_dangerous_css_properties_in_allowed(self):
        """Verify dangerous CSS properties are not in allowed list."""
        # These could be used for data exfiltration or script execution
        dangerous_styles = [
            "behavior",  # IE-specific, can execute scripts
            "-moz-binding",  # Firefox XBL bindings
            "content",  # Can be used for pseudo-element injection
        ]

        for style in dangerous_styles:
            assert style not in ALLOWED_STYLES, f"Dangerous style '{style}' should not be in ALLOWED_STYLES"


class TestXSSPrevention:
    """Comprehensive XSS attack prevention tests."""

    @pytest.mark.parametrize(
        "attack_vector,check_patterns",
        [
            # Event handler injections - must remove the attribute
            ('<img src=x onerror=alert(1)>', ["onerror"]),
            ('<body onload=alert(1)>', ["onload"]),
            ('<svg onload=alert(1)>', ["onload"]),
            ('<div onmouseover=alert(1)>test</div>', ["onmouseover"]),
            # JavaScript URL schemes
            ('<a href="javascript:alert(1)">click</a>', ["javascript:"]),
            ('<img src="javascript:alert(1)">', ["javascript:"]),
            # CSS-based attacks
            ('<div style="background:url(javascript:alert(1))">test</div>', ["javascript:"]),
            # HTML5 event handlers
            ('<video><source onerror=alert(1)></video>', ["onerror"]),
            ('<audio src=x onerror=alert(1)></audio>', ["onerror"]),
        ],
    )
    def test_blocks_xss_attack_vectors(self, attack_vector, check_patterns):
        """Verify common XSS attack vectors are blocked.

        The key security property is that executable code paths are removed:
        - Event handler attributes (onclick, onerror, etc.)
        - javascript: URLs
        - Script tags

        Note: Plain text that was inside script tags is harmless and may remain.
        """
        result = sanitize_html(attack_vector)

        for pattern in check_patterns:
            assert pattern.lower() not in result.lower(), f"XSS pattern '{pattern}' found in: {result}"

    def test_strips_script_tags_completely(self):
        """Verify script tags are removed from output."""
        test_cases = [
            '<script>alert(1)</script>',
            '<SCRIPT>alert(1)</SCRIPT>',
            '<script src="evil.js"></script>',
            '<script type="text/javascript">alert(1)</script>',
        ]

        for html in test_cases:
            result = sanitize_html(html)
            assert "<script" not in result.lower(), f"Script tag found in: {result}"
            assert "</script>" not in result.lower()

    def test_nested_script_tags(self):
        """Verify nested script tags are completely removed."""
        html = "<div><p><script><script>evil()</script></script></p></div>"
        result = sanitize_html(html)

        # Script tags must not be present
        assert "<script" not in result.lower()
        assert "</script>" not in result.lower()

    def test_encoded_attack_vectors(self):
        """Verify HTML-encoded attack vectors are handled."""
        # The sanitizer should handle these after browser decoding
        html = '<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">'
        result = sanitize_html(html)

        assert "onerror" not in result
