#!/usr/local/autopkg/python
"""
See docstring for FileImageSvgToPng class
"""

import os.path

# Requires cairosvg: python -m pip install --upgrade cairosvg
import cairosvg
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

# also needs:
# brew install cairo libffi


__all__ = ["FileImageSvgToPng"]


class FileImageSvgToPng(Processor):  # pylint: disable=too-few-public-methods
    """Convert SVG image to PNG."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "file path to image to resize",
        },
        "max_pixel_dim": {
            "required": False,
            "default": 256,
            "description": "max pixel size to resize to",
        },
        "file_path_save": {
            "required": False,
            "description": "file path to save png image",
        },
    }
    output_variables = {
        "file_path_png": {"description": "file path to png output"},
    }

    def convert_svg_to_png(self, svg_path, png_path, max_pixel_dim):
        """actual function to convert svg to png using cairosvg"""
        try:
            cairosvg.svg2png(
                url=svg_path, write_to=png_path, output_width=max_pixel_dim
            )
        except Exception as e:
            raise ProcessorError(f"Failed to convert SVG to PNG: {e}") from e

    def main(self):
        """execution starts here"""
        max_pixel_dim = int(self.env.get("max_pixel_dim", 256))
        if max_pixel_dim == 0:
            max_pixel_dim = 256
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))

        self.output(f"INFO: input file path: {file_pathname}")

        # reset file path png:
        self.env["file_path_png"] = ""
        # reset max dim to default
        self.env["max_pixel_dim"] = 256

        if file_pathname and os.path.isfile(file_pathname):
            file_path_save = self.env.get("file_path_save", f"{file_pathname}.png")

            # do conversion:
            self.convert_svg_to_png(file_pathname, file_path_save, max_pixel_dim)

            self.env["file_path_png"] = file_path_save
            self.output(f"INFO: output file path: {file_path_save}")
        else:
            self.output(f"WARNING: file does not exist! {file_pathname}", 0)


if __name__ == "__main__":
    PROCESSOR = FileImageSvgToPng()
    PROCESSOR.execute_shell()
