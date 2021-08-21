#!/usr/local/autopkg/python
"""
See docstring for FileGetBase64 class
"""

import base64

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileGetBase64"]


class FileGetBase64(Processor):  # pylint: disable=too-few-public-methods
    """Gets the file contents as base64."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "file path to base64 encode",
        },
    }
    output_variables = {
        "file_base64": {"description": "the base64 encoded string"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        if file_pathname:
            with open(file_pathname, "rb") as file_io:
                # read file and base64 encode
                file_base64 = base64.b64encode(file_io.read()).decode("utf-8")
            # get size of base64 string
            size_base64 = len(str(file_base64).encode("utf-8"))
            if size_base64 / 1024 > 64:
                self.output(
                    f"WARNING: Base64 String from File Larger than 64kb: {size_base64}",
                    0,
                )
            else:
                self.output(f"Size of Base64 String from File: { size_base64 }", 2)
            self.env["file_base64"] = file_base64


if __name__ == "__main__":
    PROCESSOR = FileGetBase64()
    PROCESSOR.execute_shell()
