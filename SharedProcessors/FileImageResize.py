#!/usr/local/autopkg/python
"""
See docstring for FileImageResize class
"""

import os.path

# Requires Pillow: python -m pip install --upgrade Pillow
from PIL import Image

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileImageResize"]


class FileImageResize(Processor):  # pylint: disable=too-few-public-methods
    """Gets the property the MSI file."""

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
            "description": "file path to save resized image",
        },
    }
    output_variables = {
        "file_path_resized": {"description": "file path to resized output"},
    }

    def main(self):
        """execution starts here"""
        max_pixel_dim = self.env.get("max_pixel_dim", 256)
        if max_pixel_dim == 0:
            max_pixel_dim = 256
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        # reset file path resized:
        self.env["file_path_resized"] = ""
        # reset max dim to default
        self.env["max_pixel_dim"] = 256

        if file_pathname and os.path.isfile(file_pathname):
            file_name, file_ext = os.path.splitext(file_pathname)
            file_path_save = self.env.get("file_path_save", f"{file_pathname}_resized{max_pixel_dim}{file_ext}")
            Image_Object = Image.open(file_pathname)
            if Image_Object.width > max_pixel_dim or Image_Object.height > max_pixel_dim:
                Image_Object.thumbnail((max_pixel_dim,max_pixel_dim),resample=Image.LANCZOS)
                Image_Object.save(file_path_save,optimize=True)
            else:
                self.output(f"WARNING: Image already smaller than {max_pixel_dim}")
                file_path_save = file_pathname
            self.env["file_path_resized"] = file_path_save
        else:
            self.output(f"WARNING: file does not exist! {file_pathname}", 0)


if __name__ == "__main__":
    PROCESSOR = FileImageResize()
    PROCESSOR.execute_shell()
