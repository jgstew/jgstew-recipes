#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileImageResize.py
#
"""See docstring for TextOnImage class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# Requires Pillow: python -m pip install --upgrade Pillow
from PIL import Image, ImageDraw, ImageFont

__all__ = ["TextOnImage"]

# Vertical margin (in pixels) from the top/bottom edge for named positions:
EDGE_MARGIN = 16


class TextOnImage(Processor):  # pylint: disable=invalid-name
    """Overlays text onto an image (with an outline for legibility) and saves the result."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the source image, defaults to %pathname%",
        },
        "text_string": {
            "required": True,
            "description": "The text to draw onto the image",
        },
        "file_path_save": {
            "required": False,
            "default": "",
            "description": (
                "Path to save the output image. Defaults to the source path with "
                "a '_text' suffix."
            ),
        },
        "font_path": {
            "required": False,
            "default": "",
            "description": (
                "Path to a .ttf/.otf font file. Defaults to Pillow's built-in font."
            ),
        },
        "font_size": {
            "required": False,
            "default": 32,
            "description": "Font size in points. Default: 32",
        },
        "text_color": {
            "required": False,
            "default": "white",
            "description": "Text fill color (name or #RRGGBB). Default: white",
        },
        "outline_color": {
            "required": False,
            "default": "black",
            "description": "Text outline color for legibility (name or #RRGGBB). Default: black",
        },
        "position": {
            "required": False,
            "default": "bottom",
            "description": (
                "Text position: 'top', 'center', 'bottom' (horizontally centered), "
                "or explicit 'x,y' pixel coordinates. Default: bottom"
            ),
        },
    }
    output_variables = {
        "file_path_text": {
            "description": "The path of the image with text drawn on it",
        },
    }
    __doc__ = description

    def load_font(self, font_path, font_size):
        """Load a TrueType font, falling back to Pillow's scalable default.

        Args:
            font_path: Path to a .ttf/.otf font file, or empty to use the default
            font_size: Font size in points

        Returns:
            A PIL ImageFont instance
        """
        if font_path:
            return ImageFont.truetype(font_path, font_size)
        return ImageFont.load_default(size=font_size)

    def resolve_position(self, position, image_size, text_size):
        """Compute the top-left (x, y) where the text should be drawn.

        Args:
            position: 'top', 'center', 'bottom', or 'x,y' coordinates
            image_size: (width, height) of the image
            text_size: (width, height) of the rendered text

        Returns:
            Tuple of (x, y) pixel coordinates
        """
        image_width, image_height = image_size
        text_width, text_height = text_size

        # explicit "x,y" coordinates:
        if "," in position:
            x_str, y_str = position.split(",", 1)
            return (int(x_str.strip()), int(y_str.strip()))

        # named positions are horizontally centered:
        x_centered = (image_width - text_width) // 2
        if position == "top":
            return (x_centered, EDGE_MARGIN)
        if position == "center":
            return (x_centered, (image_height - text_height) // 2)
        # default: bottom
        return (x_centered, image_height - text_height - EDGE_MARGIN)

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname"))
        text_string = self.env.get("text_string")
        file_path_save = self.env.get("file_path_save", "")
        font_path = self.env.get("font_path", "")
        font_size = int(self.env.get("font_size", 32))
        text_color = self.env.get("text_color", "white")
        outline_color = self.env.get("outline_color", "black")
        position = str(self.env.get("position", "bottom"))

        if not file_pathname or not os.path.isfile(file_pathname):
            raise ProcessorError(f"Image file not found: {file_pathname}")

        # default output path: source path with a _text suffix
        if not file_path_save:
            file_root, file_ext = os.path.splitext(file_pathname)
            file_path_save = f"{file_root}_text{file_ext}"

        # outline scales with font size so it stays legible at any size:
        stroke_width = max(1, font_size // 16)

        image = Image.open(file_pathname).convert("RGBA")
        draw = ImageDraw.Draw(image)
        font = self.load_font(font_path, font_size)

        # measure the rendered text (including its outline) to position it:
        text_bbox = draw.textbbox(
            (0, 0), text_string, font=font, stroke_width=stroke_width
        )
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x, text_y = self.resolve_position(
            position, image.size, (text_width, text_height)
        )

        self.output(f"Drawing text `{text_string}` at ({text_x}, {text_y})")
        draw.text(
            (text_x, text_y),
            text_string,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=outline_color,
        )

        # preserve transparency for PNGs; flatten for formats without alpha:
        save_ext = os.path.splitext(file_path_save)[1].lower()
        if save_ext in (".jpg", ".jpeg"):
            image = image.convert("RGB")
        image.save(file_path_save)

        self.output(f"Saved image with text to: {file_path_save}")

        self.env["file_path_text"] = file_path_save


if __name__ == "__main__":
    PROCESSOR = TextOnImage()
    PROCESSOR.execute_shell()
