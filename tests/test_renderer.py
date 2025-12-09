"""Integration tests for PDF rendering engine."""
import pytest
import asyncio
from app.renderer.engine import PDFRenderer
from app.renderer.page_sizes import PageSize
from config import TestConfig


@pytest.mark.integration
class TestPDFRenderer:
    """Test PDF rendering with Playwright."""

    @pytest.fixture
    def renderer(self):
        """Create renderer instance."""
        config = TestConfig()
        config.SANITIZE_HTML = False
        config.NETWORK_ISOLATION = False
        return PDFRenderer(config)

    @pytest.mark.asyncio
    async def test_render_simple_html(self, renderer, sample_html):
        """Test rendering simple HTML."""
        pdf_bytes = await renderer.render_to_pdf(
            html=sample_html,
            format='A4'
        )

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_multiple_formats(self, renderer, sample_html):
        """Test rendering with different page formats."""
        formats = ['A4', 'A3', 'LETTER', 'LEGAL']

        for format_name in formats:
            pdf_bytes = await renderer.render_to_pdf(
                html=sample_html,
                format=format_name
            )
            assert len(pdf_bytes) > 0

        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_custom_dimensions(self, renderer, sample_html):
        """Test rendering with custom dimensions."""
        pdf_bytes = await renderer.render_to_pdf(
            html=sample_html,
            width='150mm',
            height='200mm'
        )

        assert len(pdf_bytes) > 0
        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_aspect_ratios(self, renderer, sample_html):
        """Test rendering with aspect ratios."""
        aspects = ['16:9', '16:10', '4:3']

        for aspect in aspects:
            pdf_bytes = await renderer.render_to_pdf(
                html=sample_html,
                aspect=aspect
            )
            assert len(pdf_bytes) > 0

        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_with_scale(self, renderer, sample_html):
        """Test rendering with different scales."""
        pdf_bytes = await renderer.render_to_pdf(
            html=sample_html,
            format='A4',
            scale=0.5
        )

        assert len(pdf_bytes) > 0
        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_landscape(self, renderer, sample_html):
        """Test landscape orientation."""
        pdf_bytes = await renderer.render_to_pdf(
            html=sample_html,
            format='A4',
            landscape=True
        )

        assert len(pdf_bytes) > 0
        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_with_css_injection(self, renderer, sample_html):
        """Test CSS injection."""
        custom_css = """
        body { background-color: #f0f0f0; }
        h1 { color: #ff0000; }
        """

        pdf_bytes = await renderer.render_to_pdf(
            html=sample_html,
            css=custom_css
        )

        assert len(pdf_bytes) > 0
        await renderer.close()

    @pytest.mark.asyncio
    async def test_render_complex_html(self, renderer, complex_html):
        """Test rendering complex HTML with tables and gradients."""
        pdf_bytes = await renderer.render_to_pdf(
            html=complex_html,
            format='A4'
        )

        assert len(pdf_bytes) > 0
        await renderer.close()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_render_large_html(self, renderer):
        """Test rendering very large HTML."""
        # Generate large HTML
        large_html = "<html><body>"
        for i in range(100):
            large_html += f"<h2>Section {i}</h2>"
            large_html += "<p>" + ("Test content. " * 100) + "</p>"
        large_html += "</body></html>"

        pdf_bytes = await renderer.render_to_pdf(
            html=large_html,
            format='A4'
        )

        assert len(pdf_bytes) > 0
        await renderer.close()


@pytest.mark.unit
class TestPageSizeCalculations:
    """Test page size calculation logic."""

    def test_standard_formats(self):
        """Test standard paper formats."""
        calc = PageSize()

        # A4
        dims = calc.calculate_dimensions(format='A4')
        assert dims['width_mm'] == 210
        assert dims['height_mm'] == 297

        # Letter
        dims = calc.calculate_dimensions(format='LETTER')
        assert dims['width_mm'] == 215.9
        assert dims['height_mm'] == 279.4

    def test_landscape_orientation(self):
        """Test landscape orientation swaps dimensions."""
        calc = PageSize()

        dims = calc.calculate_dimensions(format='A4', landscape=True)
        assert dims['width_mm'] == 297  # Swapped
        assert dims['height_mm'] == 210

    def test_custom_dimensions(self):
        """Test custom width and height."""
        calc = PageSize()

        dims = calc.calculate_dimensions(width='100mm', height='150mm')
        assert dims['width_mm'] == 100
        assert dims['height_mm'] == 150

    def test_dimension_units(self):
        """Test different dimension units."""
        calc = PageSize(dpi=96)

        # Millimeters
        assert calc.parse_dimension('210mm') == 210

        # Inches
        assert abs(calc.parse_dimension('8.27in') - 210.058) < 0.1

        # Pixels (96 DPI)
        assert abs(calc.parse_dimension('794px') - 210.0) < 1.0

        # Centimeters
        assert calc.parse_dimension('21cm') == 210

    def test_aspect_ratios(self):
        """Test aspect ratio calculations."""
        calc = PageSize()

        # 16:9
        dims = calc.calculate_dimensions(aspect='16:9')
        ratio = dims['width_mm'] / dims['height_mm']
        assert abs(ratio - 16/9) < 0.01

        # 4:3
        dims = calc.calculate_dimensions(aspect='4:3')
        ratio = dims['width_mm'] / dims['height_mm']
        assert abs(ratio - 4/3) < 0.01

    def test_margin_parsing(self):
        """Test margin parsing."""
        calc = PageSize()

        # Single value
        margins = calc.parse_margins('10mm')
        assert margins['top'] == '10.0mm'
        assert margins['right'] == '10.0mm'

        # Four values
        margins = calc.parse_margins('10mm,20mm,30mm,40mm')
        assert margins['top'] == '10.0mm'
        assert margins['right'] == '20.0mm'
        assert margins['bottom'] == '30.0mm'
        assert margins['left'] == '40.0mm'

    def test_px_to_mm_conversion(self):
        """Test pixel to millimeter conversion at different DPIs."""
        # 96 DPI (CSS standard)
        calc96 = PageSize(dpi=96)
        mm = calc96.parse_dimension('96px')
        assert abs(mm - 25.4) < 0.1  # 1 inch = 96px @ 96dpi = 25.4mm

        # 72 DPI (print standard)
        calc72 = PageSize(dpi=72)
        mm = calc72.parse_dimension('72px')
        assert abs(mm - 25.4) < 0.1  # 1 inch = 72px @ 72dpi = 25.4mm


@pytest.mark.unit
class TestHTMLSanitizer:
    """Test HTML sanitization."""

    def test_sanitize_script_tags(self):
        """Test that script tags are removed."""
        from app.utils.sanitizer import HTMLSanitizer

        sanitizer = HTMLSanitizer(sanitize=True, allow_scripts=False)
        html = '<html><script>alert("xss")</script><p>Safe content</p></html>'
        clean = sanitizer.sanitize(html)

        assert '<script>' not in clean
        assert 'Safe content' in clean

    def test_sanitize_event_handlers(self):
        """Test that event handlers are removed."""
        from app.utils.sanitizer import HTMLSanitizer

        sanitizer = HTMLSanitizer(sanitize=True)
        html = '<div onclick="alert()">Click me</div>'
        clean = sanitizer.sanitize(html)

        assert 'onclick' not in clean

    def test_allow_scripts_option(self):
        """Test that scripts can be allowed."""
        from app.utils.sanitizer import HTMLSanitizer

        sanitizer = HTMLSanitizer(sanitize=True, allow_scripts=True)
        html = '<html><script>console.log("ok")</script></html>'
        clean = sanitizer.sanitize(html)

        assert '<script>' in clean
