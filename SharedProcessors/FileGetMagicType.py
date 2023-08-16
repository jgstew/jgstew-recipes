#!/usr/local/autopkg/python
"""
See docstring for FileGetMagicType class
"""

# MacOS:
# brew install libmagic
# Ubuntu:
# apt-get install libmagic-dev
# python module:
# python3 -m pip install --upgrade python-magic
import magic
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileGetMagicType"]


class FileGetMagicType(Processor):  # pylint: disable=too-few-public-methods
    """Gets the file magic type and mime type.
    See related: https://github.com/jgstew/tools/blob/master/Python/file_get_type_magic.py
    """

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "array of paths to find first executable within",
        },
    }
    output_variables = {
        "file_magic_type": {"description": "the file magic type"},
        "file_mime_type": {"description": "the file mime type"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))

        self.env["file_magic_type"] = str(magic.from_file(file_pathname))
        self.env["file_mime_type"] = str(magic.from_file(file_pathname, mime=True))


if __name__ == "__main__":
    PROCESSOR = FileGetMagicType()
    PROCESSOR.execute_shell()
