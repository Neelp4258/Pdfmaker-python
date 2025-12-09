"""HTML sanitization to prevent XSS and malicious content."""
import re
import logging

logger = logging.getLogger(__name__)


class HTMLSanitizer:
    """Sanitize HTML content for safe rendering."""

    # Dangerous tags to remove
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'applet',
        'meta', 'link', 'base', 'form'
    ]

    # Dangerous attributes
    DANGEROUS_ATTRS = [
        'onload', 'onerror', 'onclick', 'onmouseover',
        'onfocus', 'onblur', 'onchange', 'onsubmit'
    ]

    def __init__(self, sanitize: bool = True, allow_scripts: bool = False):
        """
        Initialize sanitizer.

        Args:
            sanitize: Whether to sanitize HTML
            allow_scripts: Whether to allow script tags
        """
        self.sanitize = sanitize
        self.allow_scripts = allow_scripts

        if allow_scripts:
            self.DANGEROUS_TAGS = [t for t in self.DANGEROUS_TAGS if t != 'script']

    def sanitize(self, html: str) -> str:
        """
        Sanitize HTML content.

        Args:
            html: Raw HTML string

        Returns:
            Sanitized HTML string
        """
        if not self.sanitize:
            return html

        # Remove dangerous tags
        for tag in self.DANGEROUS_TAGS:
            html = re.sub(
                f'<{tag}[^>]*>.*?</{tag}>',
                '',
                html,
                flags=re.IGNORECASE | re.DOTALL
            )
            html = re.sub(f'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)

        # Remove dangerous attributes
        for attr in self.DANGEROUS_ATTRS:
            html = re.sub(
                f'{attr}=(["\']).*?\\1',
                '',
                html,
                flags=re.IGNORECASE
            )

        # Remove javascript: protocol
        html = re.sub(
            r'href=["\']javascript:.*?["\']',
            '',
            html,
            flags=re.IGNORECASE
        )

        # Remove data: protocol (can be used for XSS)
        html = re.sub(
            r'src=["\']data:.*?["\']',
            '',
            html,
            flags=re.IGNORECASE
        )

        logger.debug("HTML sanitized successfully")
        return html
