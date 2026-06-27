#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileImageResize.py
#
"""See docstring for ImageToAscii class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# Requires Pillow: python -m pip install --upgrade Pillow
from PIL import Image

__all__ = ["ImageToAscii"]

# Character ramp ordered from lightest to darkest:
DEFAULT_ASCII_CHARS = " .:-=+*#%@"

# Terminal characters are roughly twice as tall as they are wide, so vertical
# resolution is scaled by this factor to keep the output from looking stretched.
CHAR_ASPECT_CORRECTION = 0.55


class ImageToAscii(Processor):  # pylint: disable=invalid-name
    """Converts an image into ASCII art, printing it to the log and returning it as a string."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the image to convert, defaults to %pathname%",
        },
        "ascii_width": {
            "required": False,
            "default": 80,
            "description": "Width of the ASCII art output in characters. Default: 80",
        },
        "ascii_chars": {
            "required": False,
            "default": DEFAULT_ASCII_CHARS,
            "description": (
                "Character ramp from lightest to darkest used to map pixel "
                f"brightness. Default: '{DEFAULT_ASCII_CHARS}'"
            ),
        },
        "ascii_invert": {
            "required": False,
            "default": False,
            "description": (
                "If True, invert brightness (useful for dark terminals). Default: False"
            ),
        },
    }
    output_variables = {
        "ascii_art": {
            "description": "The image rendered as ASCII art text",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        ascii_width = int(self.env.get("ascii_width", 80))
        ascii_chars = self.env.get("ascii_chars", DEFAULT_ASCII_CHARS)
        ascii_invert = bool(self.env.get("ascii_invert", False))

        if not file_pathname or not os.path.isfile(file_pathname):
            raise ProcessorError(f"Image file not found: {file_pathname}")

        # convert to grayscale so each pixel is a single brightness value:
        image = Image.open(file_pathname).convert("L")

        # scale height to preserve aspect ratio, correcting for character shape:
        aspect_ratio = image.height / image.width
        ascii_height = max(1, int(ascii_width * aspect_ratio * CHAR_ASPECT_CORRECTION))
        image = image.resize((ascii_width, ascii_height))

        ramp = ascii_chars[::-1] if ascii_invert else ascii_chars
        ramp_max_index = len(ramp) - 1

        pixels = list(image.getdata())
        ascii_rows = []
        for row_start in range(0, len(pixels), ascii_width):
            row_pixels = pixels[row_start : row_start + ascii_width]
            # map each 0-255 brightness onto an index in the character ramp:
            row_chars = [
                ramp[brightness * ramp_max_index // 255] for brightness in row_pixels
            ]
            ascii_rows.append("".join(row_chars))
        ascii_art = "\n".join(ascii_rows)

        self.output(f"ASCII art for: {file_pathname}")
        self.output("\n" + ascii_art)

        self.env["ascii_art"] = ascii_art


if __name__ == "__main__":
    PROCESSOR = ImageToAscii()
    PROCESSOR.execute_shell()
