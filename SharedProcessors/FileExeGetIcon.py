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
    """Extracts a numbered icon resource from a Windows PE file and saves it as an .ico file using icoextract."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Windows PE File to get the icon from.",
        },
        "icon_file_output": {
            "required": False,
            "description": "File to save the icon to.",
        },
        "icon_file_number": {
            "required": False,
            "default": 0,
            "description": "Numbered index of the icon to get.",
        },
    }
    output_variables = {
        "icon_file_output": {
            "description": "The file path where the extracted icon was saved"
        },
    }

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))

        icon_file_output = self.env.get("icon_file_output", None)
        # default output to "%RECIPE_CACHE_DIR%/%NAME%.ico" if unset
        if not icon_file_output:
            icon_file_output = (
                self.env.get("RECIPE_CACHE_DIR", "")
                + "/"
                + self.env.get("NAME", "file")
                + ".ico"
            )
            self.env["icon_file_output"] = icon_file_output
        icon_file_number = int(self.env.get("icon_file_number", 0))

        icoExtInst = icoextract.IconExtractor(file_pathname)
        icoExtInst.export_icon(icon_file_output, num=icon_file_number)


if __name__ == "__main__":
    PROCESSOR = FileExeGetIcon()
    PROCESSOR.execute_shell()
