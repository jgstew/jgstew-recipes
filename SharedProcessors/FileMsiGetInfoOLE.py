#!/usr/local/autopkg/python
"""
See docstring for FileMsiGetInfoOLE class
"""

# pip install olefile
import olefile
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileMsiGetInfoOLE"]


class FileMsiGetInfoOLE(Processor):  # pylint: disable=too-few-public-methods
    """Get info from an OLE file (MSI)
    See related: https://github.com/jgstew/tools/blob/master/Python/file_msi_get_info_ole.py
    """

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Windows PE File to get the info from.",
        },
        "custom_oleinfo_index": {
            "required": False,
            "default": "author",
            "description": "Custom index to retrieve, defaults to `author`",
        },
        "custom_oleinfo_output": {
            "required": False,
            "default": "olefile_author",
            "description": "Variable to store the output to, defaults to `olefile_author`",
        },
    }
    output_variables = {
        "file_olefile_last_saved_time": {"description": "last_saved_time"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        verbose = self.env.get("verbose", 3)

        oleinfo = olefile.OleFileIO(file_pathname)
        meta = oleinfo.get_metadata()

        if verbose > 2:
            print("MSI OLE Summary Info Dump:")
            meta.dump()

        self.output("TODO: implement!", 0)

        """
        Example OLEInfo:
            ('codepage', 1252)
            ('title', b'Installation Database')
            ('subject', b'PowerShell package')
            ('author', b'Microsoft Corporation')
            ('keywords', b'Installer')
            ('comments', b'PowerShell for every system')
            ('template', b'x64;1033')
            ('last_saved_by', None)
            ('revision_number', b'{1C2D9348-D125-49E4-9A02-622883308386}')
            ('total_edit_time', None)
            ('last_printed', None)
            ('create_time', datetime.datetime(2022, 6, 15, 17, 39, 24))
            ('last_saved_time', datetime.datetime(2022, 6, 15, 17, 39, 24))
            ('num_pages', 200)
            ('num_words', 2)
            ('num_chars', None)
            ('thumbnail', None)
            ('creating_application', b'Windows Installer XML Toolset (3.11.2.4516)')
            ('security', 2)
        """


if __name__ == "__main__":
    PROCESSOR = FileMsiGetInfoOLE()
    PROCESSOR.execute_shell()
