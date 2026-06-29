#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileImageResize.py
#
"""See docstring for ColorThief class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# Requires Pillow: python -m pip install --upgrade Pillow
from PIL import Image

__all__ = ["ColorThief"]

# Resize the image to this max dimension before analysis for speed; color
# proportions are preserved well enough for dominant-color detection.
ANALYSIS_MAX_DIM = 100


def rgb_to_hex(rgb):
    """Convert an (r, g, b) sequence to a #RRGGBB hex string.

    Args:
        rgb: Sequence of three 0-255 integers

    Returns:
        Hex color string like '#aabbcc'
    """
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


class ColorThief(Processor):  # pylint: disable=invalid-name
    """Extracts the dominant color and a small color palette from an image using Pillow."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the image to analyze, defaults to %pathname%",
        },
        "color_count": {
            "required": False,
            "default": 5,
            "description": "Number of palette colors to quantize the image into. Default: 5",
        },
    }
    output_variables = {
        "dominant_color_hex": {
            "description": "The most common color as a #RRGGBB hex string",
        },
        "dominant_color_rgb": {
            "description": "The most common color as a comma-separated 'r,g,b' string",
        },
        "palette_colors": {
            "description": "Array of palette colors as #RRGGBB hex strings, most common first",
        },
    }
    __doc__ = description

    def get_palette(self, image, color_count):
        """Quantize an image and return its palette ordered by pixel frequency.

        Args:
            image: A PIL Image (any mode)
            color_count: Number of palette colors to reduce to

        Returns:
            List of (r, g, b) tuples ordered from most to least common
        """
        rgb_image = image.convert("RGB")
        # shrink for speed; proportions are preserved well enough:
        rgb_image.thumbnail((ANALYSIS_MAX_DIM, ANALYSIS_MAX_DIM))

        quantized = rgb_image.quantize(colors=color_count, method=Image.MEDIANCUT)
        palette = quantized.getpalette()

        # getcolors() -> list of (count, palette_index); sort most common first:
        color_counts = sorted(quantized.getcolors(), reverse=True)

        ordered_palette = []
        for _count, palette_index in color_counts:
            start = palette_index * 3
            ordered_palette.append(tuple(palette[start : start + 3]))
        return ordered_palette

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        file_pathname = self.env.get("file_pathname", self.env.get("pathname"))
        color_count = int(self.env.get("color_count", 5))

        # Running Process
        if not file_pathname or not os.path.isfile(file_pathname):
            raise ProcessorError(f"Image file not found: {file_pathname}")

        image = Image.open(file_pathname)
        ordered_palette = self.get_palette(image, color_count)

        if not ordered_palette:
            raise ProcessorError(f"Could not extract any colors from: {file_pathname}")

        dominant_rgb = ordered_palette[0]
        palette_hex = [rgb_to_hex(rgb) for rgb in ordered_palette]

        self.output(f"Dominant color: {rgb_to_hex(dominant_rgb)} {dominant_rgb}")
        self.output(f"Palette: {palette_hex}", 2)

        # Writing output_variables
        self.env["dominant_color_hex"] = rgb_to_hex(dominant_rgb)
        self.env["dominant_color_rgb"] = ",".join(str(int(c)) for c in dominant_rgb)
        self.env["palette_colors"] = palette_hex


if __name__ == "__main__":
    PROCESSOR = ColorThief()
    PROCESSOR.execute_shell()
