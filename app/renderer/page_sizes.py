"""
Page size calculations with precise mm/in/px conversions.
Supports named formats, custom dimensions, and aspect ratios.
"""
from typing import Dict, Optional, Tuple
import re


# Standard paper formats in mm (width, height)
STANDARD_FORMATS = {
    'A4': (210, 297),
    'A3': (297, 420),
    'A2': (420, 594),
    'A5': (148, 210),
    'LETTER': (215.9, 279.4),
    'LEGAL': (215.9, 355.6),
    'TABLOID': (279.4, 431.8),
    'LEDGER': (431.8, 279.4),
    'RECEIPT': (80, 297),  # Thermal receipt, variable height
}

# Common aspect ratios
ASPECT_RATIOS = {
    '16:9': 16 / 9,
    '16:10': 16 / 10,
    '4:3': 4 / 3,
    '3:2': 3 / 2,
    '1:1': 1,
}


class PageSize:
    """Calculate exact page dimensions for PDF rendering."""

    def __init__(self, dpi: int = 96):
        """
        Initialize page size calculator.

        Args:
            dpi: Dots per inch for pixel calculations (default 96 for CSS)
        """
        self.dpi = dpi
        self.mm_per_inch = 25.4

    def parse_dimension(self, value: str) -> float:
        """
        Parse dimension string to millimeters.

        Args:
            value: Dimension like "10mm", "2in", "800px", "10.5cm"

        Returns:
            Dimension in millimeters
        """
        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip().lower()

        # Extract number and unit
        match = re.match(r'([\d.]+)\s*([a-z]*)', value)
        if not match:
            raise ValueError(f"Invalid dimension format: {value}")

        num, unit = match.groups()
        num = float(num)

        # Convert to mm
        if unit in ('mm', ''):
            return num
        elif unit == 'cm':
            return num * 10
        elif unit in ('in', 'inch'):
            return num * self.mm_per_inch
        elif unit == 'px':
            return num * self.mm_per_inch / self.dpi
        elif unit == 'pt':
            return num * self.mm_per_inch / 72
        else:
            raise ValueError(f"Unknown unit: {unit}")

    def get_standard_format(self, format_name: str, landscape: bool = False) -> Tuple[float, float]:
        """
        Get dimensions for standard paper format.

        Args:
            format_name: Paper format (A4, Letter, etc.)
            landscape: Whether to rotate to landscape orientation

        Returns:
            Tuple of (width_mm, height_mm)
        """
        format_name = format_name.upper()

        if format_name not in STANDARD_FORMATS:
            raise ValueError(f"Unknown format: {format_name}. Available: {', '.join(STANDARD_FORMATS.keys())}")

        width, height = STANDARD_FORMATS[format_name]

        if landscape:
            return (height, width)

        return (width, height)

    def apply_aspect_ratio(self, aspect: str, base_dimension: Optional[str] = None) -> Tuple[float, float]:
        """
        Calculate dimensions from aspect ratio.

        Args:
            aspect: Aspect ratio like "16:9", "16:10", "4:3"
            base_dimension: Optional base width or height to constrain to

        Returns:
            Tuple of (width_mm, height_mm)
        """
        if aspect not in ASPECT_RATIOS:
            # Try parsing custom aspect ratio
            match = re.match(r'(\d+):(\d+)', aspect)
            if not match:
                raise ValueError(f"Invalid aspect ratio: {aspect}")
            ratio = int(match.group(1)) / int(match.group(2))
        else:
            ratio = ASPECT_RATIOS[aspect]

        # Default to A4 width if no base dimension
        if not base_dimension:
            width_mm = 210  # A4 width
            height_mm = width_mm / ratio
        else:
            base_mm = self.parse_dimension(base_dimension)
            # Assume base is width for landscape ratios (>1), height otherwise
            if ratio > 1:
                width_mm = base_mm
                height_mm = base_mm / ratio
            else:
                height_mm = base_mm
                width_mm = base_mm * ratio

        return (width_mm, height_mm)

    def calculate_dimensions(
        self,
        format: Optional[str] = None,
        width: Optional[str] = None,
        height: Optional[str] = None,
        aspect: Optional[str] = None,
        landscape: bool = False
    ) -> Dict[str, float]:
        """
        Calculate final page dimensions based on various inputs.

        Priority:
        1. Explicit width + height
        2. Format name (A4, Letter, etc.)
        3. Aspect ratio with optional base dimension

        Args:
            format: Named format (A4, Letter, etc.)
            width: Width dimension
            height: Height dimension
            aspect: Aspect ratio (16:9, etc.)
            landscape: Rotate to landscape

        Returns:
            Dict with width_mm, height_mm, width_px, height_px, width_in, height_in
        """
        width_mm, height_mm = None, None

        # Priority 1: Explicit dimensions
        if width and height:
            width_mm = self.parse_dimension(width)
            height_mm = self.parse_dimension(height)

        # Priority 2: Named format
        elif format:
            width_mm, height_mm = self.get_standard_format(format, landscape)

        # Priority 3: Aspect ratio
        elif aspect:
            base = width or height
            width_mm, height_mm = self.apply_aspect_ratio(aspect, base)

        # Default to A4
        else:
            width_mm, height_mm = self.get_standard_format('A4', landscape)

        # Convert to other units
        width_in = width_mm / self.mm_per_inch
        height_in = height_mm / self.mm_per_inch
        width_px = width_in * self.dpi
        height_px = height_in * self.dpi

        return {
            'width_mm': width_mm,
            'height_mm': height_mm,
            'width_in': width_in,
            'height_in': height_in,
            'width_px': int(width_px),
            'height_px': int(height_px),
        }

    def parse_margins(self, margin: Optional[str]) -> Dict[str, str]:
        """
        Parse margin specification to CSS format.

        Args:
            margin: Margin like "10mm" or "10mm,20mm,10mm,20mm" (top,right,bottom,left)

        Returns:
            Dict with top, right, bottom, left in mm
        """
        if not margin:
            return {'top': '0mm', 'right': '0mm', 'bottom': '0mm', 'left': '0mm'}

        parts = [m.strip() for m in margin.split(',')]

        if len(parts) == 1:
            # All sides same
            m = f"{self.parse_dimension(parts[0])}mm"
            return {'top': m, 'right': m, 'bottom': m, 'left': m}
        elif len(parts) == 2:
            # top/bottom, left/right
            tb = f"{self.parse_dimension(parts[0])}mm"
            lr = f"{self.parse_dimension(parts[1])}mm"
            return {'top': tb, 'right': lr, 'bottom': tb, 'left': lr}
        elif len(parts) == 4:
            # top, right, bottom, left
            return {
                'top': f"{self.parse_dimension(parts[0])}mm",
                'right': f"{self.parse_dimension(parts[1])}mm",
                'bottom': f"{self.parse_dimension(parts[2])}mm",
                'left': f"{self.parse_dimension(parts[3])}mm",
            }
        else:
            raise ValueError(f"Invalid margin format: {margin}")
