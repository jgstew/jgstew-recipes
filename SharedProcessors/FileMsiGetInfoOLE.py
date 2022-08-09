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
            "default": "file_ole_author",
            "description": "Variable to store the output to, defaults to `file_ole_author`",
        },
    }
    output_variables = {
        "file_ole_max_time": {"description": "max creation last_saved time"},
        "file_ole_create_time": {"description": "create_time"},
        "file_ole_last_saved_time": {"description": "last_saved_time"},
        "SourceReleaseDate": {"description": "max creation last_saved time yyyy-mm-dd"},
    }

    def get_ole_max_time(self, ole_metadata):
        """get max of creation and last_saved time"""
        dates_to_compare = []

        # get create_time
        create_time = getattr(ole_metadata, "create_time")
        self.env["file_ole_create_time"] = create_time
        dates_to_compare.append(create_time)

        # get last_saved_time
        last_saved_time = getattr(ole_metadata, "last_saved_time")
        self.env["file_ole_last_saved_time"] = last_saved_time
        dates_to_compare.append(last_saved_time)

        max_time = max(dates_to_compare)
        self.env["file_ole_max_time"] = str(max_time)
        self.env["SourceReleaseDate"] = max_time.strftime("%Y-%m-%d")

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        custom_oleinfo_index = self.env.get("custom_oleinfo_index", None)
        custom_oleinfo_output = self.env.get("custom_oleinfo_output", None)
        verbose = self.env.get("verbose", 3)

        oleinfo = olefile.OleFileIO(file_pathname)
        ole_metadata = oleinfo.get_metadata()
        self.get_ole_max_time(ole_metadata)

        self.env[custom_oleinfo_output] = str(
            getattr(ole_metadata, custom_oleinfo_index).decode()
        )

        if verbose > 3:
            print("MSI OLE Summary Info Dump:")
            ole_metadata.dump()

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
