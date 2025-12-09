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
        # Support both dict-style and attribute-style config access
        default_dpi = self._get_config('DEFAULT_DPI', 96)
        sanitize_html = self._get_config('SANITIZE_HTML', True)
        allow_scripts = self._get_config('ALLOW_INLINE_SCRIPTS', False)

        self.page_size_calc = PageSize(dpi=default_dpi)
        self.sanitizer = HTMLSanitizer(
            sanitize=sanitize_html,
            allow_scripts=allow_scripts
        )
        self.browser: Optional[Browser] = None

    def _get_config(self, key: str, default: Any = None) -> Any:
        """
        Safely get config value supporting both dict and attribute access.

        Args:
            key: Config key name
            default: Default value if key not found

        Returns:
            Config value
        """
        # Try dict-style access first (Flask config)
        if hasattr(self.config, 'get'):
            return self.config.get(key, default)
        # Fall back to attribute access (Config class)
        return getattr(self.config, key, default)

    async def _get_browser(self) -> Browser:
        """Get or create browser instance."""
        if self.browser is None or not self.browser.is_connected():
            logger.info("Starting Playwright and launching Chromium browser...")
            try:
                playwright = await async_playwright().start()
                logger.debug("Playwright started successfully")

                chromium_args = self._get_config('CHROMIUM_ARGS', [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                ])
                logger.debug(f"Launching browser with args: {chromium_args}")

                self.browser = await playwright.chromium.launch(
                    headless=True,
                    args=chromium_args
                )
                logger.info("Chromium browser launched successfully")
            except Exception as e:
                logger.error(f"Failed to start browser: {e}", exc_info=True)
                raise RuntimeError(f"Failed to initialize browser: {str(e)}") from e
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
        if not self._get_config('ALLOW_URL_RENDERING', True):
            raise ValueError("URL rendering is disabled")

        # Extract hostname
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname or parsed.netloc

        # Check denylist (SSRF protection)
        url_denylist = self._get_config('URL_DENYLIST', ['127.0.0.1', 'localhost', '0.0.0.0'])
        for denied in url_denylist:
            if denied in hostname:
                raise ValueError(f"URL blocked by denylist: {hostname}")

        # Check allowlist if configured
        url_allowlist = self._get_config('URL_ALLOWLIST', [])
        if url_allowlist:
            allowed = any(pattern in hostname for pattern in url_allowlist)
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
            logger.debug("Getting browser instance...")
            browser = await self._get_browser()
            logger.debug("Browser instance obtained")

            context_options = {}

            # Set custom headers if provided
            if headers:
                context_options['extra_http_headers'] = headers

            # Network isolation for security
            if self._get_config('NETWORK_ISOLATION', False) and html:
                context_options['offline'] = True

            logger.debug("Creating browser context...")
            context = await browser.new_context(**context_options)
            logger.debug("Browser context created")

            # Disable JavaScript if configured
            if self._get_config('DISABLE_JAVASCRIPT', False):
                await context.add_init_script("() => { Object.freeze(Object.prototype); }")

            logger.debug("Creating new page...")
            page = await context.new_page()
            logger.debug("New page created")

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
            chromium_timeout = self._get_config('CHROMIUM_TIMEOUT', 30000)
            if html:
                logger.debug("Loading HTML content...")
                # Sanitize HTML if configured
                if self._get_config('SANITIZE_HTML', True):
                    logger.debug("Sanitizing HTML...")
                    html = self.sanitizer.sanitize(html)

                # Inject CSS into HTML
                if '<head>' in html:
                    html = html.replace('<head>', f'<head>{page_css}')
                else:
                    html = f'{page_css}{html}'

                logger.debug(f"Setting page content (timeout: {chromium_timeout}ms)...")
                # Use 'domcontentloaded' instead of 'networkidle' to prevent hanging
                await page.set_content(html, wait_until='domcontentloaded', timeout=chromium_timeout)
                logger.debug("Page content set successfully")
            else:
                logger.debug(f"Navigating to URL: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=chromium_timeout)
                logger.debug("URL navigation complete")

                # Inject CSS for URL rendering
                await page.add_style_tag(content=page_css)
                if css:
                    await page.add_style_tag(content=css)

            # Wait for specific selector or timeout
            if wait_for:
                logger.debug(f"Waiting for: {wait_for}")
                if wait_for.isdigit():
                    await asyncio.sleep(int(wait_for) / 1000)
                else:
                    await page.wait_for_selector(wait_for, timeout=chromium_timeout)
                logger.debug("Wait condition met")

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
            logger.debug("Generating PDF from page...")
            logger.debug(f"PDF options: {pdf_options}")
            pdf_bytes = await page.pdf(**pdf_options)
            logger.debug(f"PDF bytes generated: {len(pdf_bytes)} bytes")

            logger.debug("Closing browser context...")
            await context.close()
            logger.debug("Browser context closed")

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


# Global browser instance cache (reused across requests for performance)
_browser_cache = {}

# Synchronous wrapper for non-async contexts
def render_pdf_sync(*args, **kwargs) -> bytes:
    """Synchronous wrapper for PDF rendering."""
    logger.debug("render_pdf_sync called")
    config = kwargs.pop('config')
    renderer = PDFRenderer(config)

    async def _render():
        """Async function to render PDF without closing browser (reuse for performance)."""
        try:
            logger.debug("Starting PDF rendering in async context...")
            pdf_bytes = await renderer.render_to_pdf(*args, **kwargs)
            logger.debug(f"PDF rendering completed, got {len(pdf_bytes)} bytes")
            return pdf_bytes
        except Exception as e:
            # Only close browser on errors to reset state
            logger.warning("Error during rendering, closing browser to reset state")
            try:
                await renderer.close()
            except:
                pass
            raise

    try:
        logger.debug("Starting asyncio.run for PDF rendering...")
        pdf_bytes = asyncio.run(_render())
        logger.debug("asyncio.run completed successfully")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error in render_pdf_sync: {e}", exc_info=True)
        raise
