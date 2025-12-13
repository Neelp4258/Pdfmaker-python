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
        self.enabled = sanitize
        self.allow_scripts = allow_scripts

        if allow_scripts:
            self.DANGEROUS_TAGS = [t for t in self.DANGEROUS_TAGS if t != 'script']

    def _detect_hosted_images(self, html: str) -> None:
        """
        Detect and log hosted images (http/https URLs) in HTML.

        Args:
            html: HTML string to analyze
        """
        # Pattern to match img tags with http/https src
        img_pattern = r'<img[^>]+src=["\']?(https?://[^"\'>\s]+)["\']?[^>]*>'

        hosted_images = re.findall(img_pattern, html, flags=re.IGNORECASE)

        if hosted_images:
            logger.info(f"🖼️  Found {len(hosted_images)} hosted image(s) in HTML:")
            for idx, img_url in enumerate(hosted_images, 1):
                logger.info(f"  [{idx}] {img_url}")
            print(f"\n{'='*60}")
            print(f"🖼️  HOSTED IMAGES DETECTED: {len(hosted_images)} image(s)")
            print(f"{'='*60}")
            for idx, img_url in enumerate(hosted_images, 1):
                print(f"  [{idx}] {img_url}")
            print(f"{'='*60}\n")
        else:
            logger.debug("No hosted images (http/https) found in HTML")

    def sanitize(self, html: str) -> str:
        """
        Sanitize HTML content.

        Args:
            html: Raw HTML string

        Returns:
            Sanitized HTML string
        """
        if not self.enabled:
            # Still detect images even if sanitization is disabled
            self._detect_hosted_images(html)
            return html

        # Detect hosted images before sanitization
        self._detect_hosted_images(html)

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
