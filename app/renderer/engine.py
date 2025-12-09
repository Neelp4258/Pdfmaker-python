"""
Playwright-based PDF rendering engine with pixel-perfect output.
Supports multi-page content, custom CSS, and exact page dimensions.
"""
import asyncio
import logging
from typing import Dict, Optional, Any
from playwright.async_api import async_playwright, Browser, Page
from app.renderer.page_sizes import PageSize
from app.utils.sanitizer import HTMLSanitizer
import re

logger = logging.getLogger(__name__)


class PDFRenderer:
    """
    Headless Chromium PDF renderer using Playwright.
    Provides pixel-perfect rendering with exact page sizes.
    """

    def __init__(self, config: Any):
        """
        Initialize PDF renderer.

        Args:
            config: Application configuration object
        """
        self.config = config
        self.page_size_calc = PageSize(dpi=config.DEFAULT_DPI)
        self.sanitizer = HTMLSanitizer(
            sanitize=config.SANITIZE_HTML,
            allow_scripts=config.ALLOW_INLINE_SCRIPTS
        )
        self.browser: Optional[Browser] = None

    async def _get_browser(self) -> Browser:
        """Get or create browser instance."""
        if self.browser is None or not self.browser.is_connected():
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=self.config.CHROMIUM_ARGS
            )
        return self.browser

    async def close(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
            self.browser = None

    def _build_page_css(self, dimensions: Dict, margin: Dict, scale: float = 1.0) -> str:
        """
        Build CSS @page rules and print styles for exact rendering.

        Args:
            dimensions: Page dimensions dict
            margin: Margin dict
            scale: Page scale factor

        Returns:
            CSS string to inject
        """
        css = f"""
        <style>
            /* @page rules for exact PDF dimensions */
            @page {{
                size: {dimensions['width_mm']}mm {dimensions['height_mm']}mm;
                margin-top: {margin['top']};
                margin-right: {margin['right']};
                margin-bottom: {margin['bottom']};
                margin-left: {margin['left']};
            }}

            /* Ensure backgrounds and colors are printed */
            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }}

            /* Body sizing */
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
            }}

            /* Respect CSS page-break properties */
            .page-break {{
                page-break-after: always;
                break-after: page;
            }}

            .no-break {{
                page-break-inside: avoid;
                break-inside: avoid;
            }}
        </style>
        """
        return css

    def _validate_url(self, url: str) -> bool:
        """
        Validate URL against allowlist/denylist for SSRF protection.

        Args:
            url: URL to validate

        Returns:
            True if URL is allowed

        Raises:
            ValueError if URL is not allowed
        """
        if not self.config.ALLOW_URL_RENDERING:
            raise ValueError("URL rendering is disabled")

        # Extract hostname
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname or parsed.netloc

        # Check denylist (SSRF protection)
        for denied in self.config.URL_DENYLIST:
            if denied in hostname:
                raise ValueError(f"URL blocked by denylist: {hostname}")

        # Check allowlist if configured
        if self.config.URL_ALLOWLIST:
            allowed = any(pattern in hostname for pattern in self.config.URL_ALLOWLIST)
            if not allowed:
                raise ValueError(f"URL not in allowlist: {hostname}")

        return True

    async def render_to_pdf(
        self,
        html: Optional[str] = None,
        url: Optional[str] = None,
        format: str = 'A4',
        width: Optional[str] = None,
        height: Optional[str] = None,
        aspect: Optional[str] = None,
        landscape: bool = False,
        margin: Optional[str] = None,
        scale: float = 1.0,
        page_ranges: Optional[str] = None,
        css: Optional[str] = None,
        wait_for: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """
        Render HTML or URL to PDF with exact dimensions.

        Args:
            html: HTML content string (mutually exclusive with url)
            url: URL to render (mutually exclusive with html)
            format: Named format (A4, Letter, etc.)
            width: Custom width (e.g., "210mm", "8.5in", "800px")
            height: Custom height
            aspect: Aspect ratio (e.g., "16:9", "4:3")
            landscape: Rotate to landscape
            margin: Margins (e.g., "10mm" or "10mm,20mm,10mm,20mm")
            scale: Page scale factor (0.1 to 2.0)
            page_ranges: Page ranges to print (e.g., "1-5, 8, 11-13")
            css: Additional CSS to inject
            wait_for: Selector to wait for or timeout in ms (e.g., "#content" or "5000")
            headers: HTTP headers for URL requests

        Returns:
            PDF bytes

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If rendering fails
        """
        # Validate input
        if not html and not url:
            raise ValueError("Either html or url must be provided")
        if html and url:
            raise ValueError("Provide either html or url, not both")

        # Validate URL if provided
        if url:
            self._validate_url(url)

        # Calculate page dimensions
        dimensions = self.page_size_calc.calculate_dimensions(
            format=format,
            width=width,
            height=height,
            aspect=aspect,
            landscape=landscape
        )

        # Parse margins
        margins = self.page_size_calc.parse_margins(margin)

        logger.info(f"Rendering PDF: {dimensions['width_mm']}x{dimensions['height_mm']}mm, scale={scale}")

        try:
            browser = await self._get_browser()
            context_options = {}

            # Set custom headers if provided
            if headers:
                context_options['extra_http_headers'] = headers

            # Network isolation for security
            if self.config.NETWORK_ISOLATION and html:
                context_options['offline'] = True

            context = await browser.new_context(**context_options)

            # Disable JavaScript if configured
            if self.config.DISABLE_JAVASCRIPT:
                await context.add_init_script("() => { Object.freeze(Object.prototype); }")

            page = await context.new_page()

            # Set viewport to match page dimensions
            await page.set_viewport_size({
                'width': dimensions['width_px'],
                'height': dimensions['height_px']
            })

            # Build and inject CSS
            page_css = self._build_page_css(dimensions, margins, scale)
            if css:
                page_css += f"\n<style>{css}</style>"

            # Load content
            if html:
                # Sanitize HTML if configured
                if self.config.SANITIZE_HTML:
                    html = self.sanitizer.sanitize(html)

                # Inject CSS into HTML
                if '<head>' in html:
                    html = html.replace('<head>', f'<head>{page_css}')
                else:
                    html = f'{page_css}{html}'

                await page.set_content(html, wait_until='networkidle', timeout=self.config.CHROMIUM_TIMEOUT)
            else:
                await page.goto(url, wait_until='networkidle', timeout=self.config.CHROMIUM_TIMEOUT)

                # Inject CSS for URL rendering
                await page.add_style_tag(content=page_css)
                if css:
                    await page.add_style_tag(content=css)

            # Wait for specific selector or timeout
            if wait_for:
                if wait_for.isdigit():
                    await asyncio.sleep(int(wait_for) / 1000)
                else:
                    await page.wait_for_selector(wait_for, timeout=self.config.CHROMIUM_TIMEOUT)

            # Prepare PDF options
            pdf_options = {
                'width': f'{dimensions["width_mm"]}mm',
                'height': f'{dimensions["height_mm"]}mm',
                'margin': margins,
                'scale': scale,
                'print_background': True,
                'prefer_css_page_size': True,
            }

            if page_ranges:
                pdf_options['page_ranges'] = page_ranges

            # Generate PDF
            pdf_bytes = await page.pdf(**pdf_options)

            await context.close()

            logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF rendering failed: {e}", exc_info=True)
            raise RuntimeError(f"PDF rendering failed: {str(e)}") from e

    async def render_batch(self, jobs: list) -> list:
        """
        Render multiple PDFs in batch (reuses browser).

        Args:
            jobs: List of job dicts with render parameters

        Returns:
            List of PDF bytes
        """
        results = []
        try:
            for job in jobs:
                pdf = await self.render_to_pdf(**job)
                results.append(pdf)
        finally:
            await self.close()

        return results


# Synchronous wrapper for non-async contexts
def render_pdf_sync(*args, **kwargs) -> bytes:
    """Synchronous wrapper for PDF rendering."""
    renderer = PDFRenderer(kwargs.pop('config'))
    try:
        return asyncio.run(renderer.render_to_pdf(*args, **kwargs))
    finally:
        asyncio.run(renderer.close())
