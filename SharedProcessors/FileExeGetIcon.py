#!/usr/local/autopkg/python
"""
See docstring for FileExeGetIcon class
"""

# pip install icoextract
import icoextract
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileExeGetIcon"]


class FileExeGetIcon(Processor):  # pylint: disable=too-few-public-methods
    """Get the icon from a PEFile
    See related: https://github.com/jgstew/tools/blob/master/Python/file_get_icon_exe_icoextract.py
    """

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Windows PE File to get the icon from.",
        },
        "icon_file_output": {
            "required": True,
            "description": "File to save the icon to.",
        },
        "icon_file_number": {
            "required": False,
            "default": 0,
            "description": "Numbered index of the icon to get.",
        },
    }
    output_variables = {
        "icon_file_output": {"description": "File to save the icon to."},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        icon_file_output = self.env.get("icon_file_output", None)
        icon_file_number = int(self.env.get("icon_file_number", 0))

        icoExtInst = icoextract.IconExtractor(file_pathname)
        icoExtInst.export_icon(icon_file_output, num=icon_file_number)


if __name__ == "__main__":
    PROCESSOR = FileExeGetIcon()
    PROCESSOR.execute_shell()
