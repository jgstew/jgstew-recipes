#!/usr/local/autopkg/python
"""
See docstring for FileExeGetInfoPE class
"""

# pip install pefile
import pefile
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileExeGetInfoPE"]


def dump_info_pefile(filepath, first_only=True):
    """dump pefile info StringTable

    Originally from:
    - https://github.com/jgstew/tools/blob/master/Python/file_get_version_exe_pefile.py
    """
    pe = pefile.PE(filepath)

    pe_info_dict = {}

    if hasattr(pe, "VS_VERSIONINFO"):
        for idx in range(len(pe.VS_VERSIONINFO)):
            if hasattr(pe, "FileInfo") and len(pe.FileInfo) > idx:
                for entry in pe.FileInfo[idx]:
                    if hasattr(entry, "StringTable"):
                        for st_entry in entry.StringTable:
                            for str_entry in sorted(list(st_entry.entries.items())):
                                pe_info_dict[
                                    str_entry[0].decode("utf-8", "backslashreplace")
                                ] = str_entry[1].decode("utf-8", "backslashreplace")
                            if first_only:
                                return pe_info_dict
    return pe_info_dict


class FileExeGetInfoPE(Processor):  # pylint: disable=too-few-public-methods
    """Get info from a PEFile
    See related: https://github.com/jgstew/tools/blob/master/Python/file_get_version_exe_pefile.py
    """

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Windows PE File to get the info from.",
        },
        "custom_peinfo_index": {
            "required": False,
            "default": "FileVersion",
            "description": "Custom index to retrieve, defaults to `FileVersion`",
        },
        "custom_peinfo_output": {
            "required": False,
            "default": "version",
            "description": "Variable to store the output to, defaults to `version`",
        },
        "peinfo_first_only": {
            "required": False,
            "default": True,
            "description": "If True, return first version info found. If False, return last.",
        },
    }
    output_variables = {
        "file_peinfo_FileVersion": {"description": "FileVersion"},
        "file_peinfo_ProductVersion": {"description": "ProductVersion"},
        "file_peinfo_ProductName": {"description": "ProductName"},
        "file_peinfo_CompanyName": {"description": "CompanyName"},
        "file_peinfo_FileDescription": {"description": "FileDescription"},
        "file_peinfo_InternalName": {"description": "InternalName"},
        "file_peinfo_OriginalFilename": {"description": "OriginalFilename"},
        "file_peinfo_LegalCopyright": {"description": "LegalCopyright"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        custom_peinfo_index = self.env.get("custom_peinfo_index", "FileVersion")
        custom_peinfo_output = self.env.get("custom_peinfo_output", "version")
        peinfo_first_only = self.env.get("peinfo_first_only", True)

        pe_info_dict = dump_info_pefile(file_pathname, peinfo_first_only)

        self.output(f"Info: full pe_info: {pe_info_dict}", 4)

        try:
            self.env[custom_peinfo_output] = pe_info_dict[custom_peinfo_index].strip()
            self.output_variables[custom_peinfo_output] = {
                "description": f"custom {custom_peinfo_index} output"
            }
        except KeyError:
            self.output(f"Info: Missing {custom_peinfo_index}")
            self.env[custom_peinfo_output] = ""

        try:
            self.env["file_peinfo_FileVersion"] = pe_info_dict["FileVersion"].strip()
        except KeyError:
            self.output("Info: Missing FileVersion")
            self.env["file_peinfo_FileVersion"] = ""

        try:
            self.env["file_peinfo_ProductVersion"] = pe_info_dict[
                "ProductVersion"
            ].strip()
        except KeyError:
            self.output("Info: Missing ProductVersion")
            self.env["file_peinfo_ProductVersion"] = ""

        try:
            self.env["file_peinfo_ProductName"] = pe_info_dict["ProductName"].strip()
        except KeyError:
            self.output("Info: Missing ProductName")
            self.env["file_peinfo_ProductName"] = ""

        try:
            self.env["file_peinfo_CompanyName"] = pe_info_dict["CompanyName"].strip()
        except KeyError:
            self.output("Info: Missing CompanyName")
            self.env["file_peinfo_CompanyName"] = ""

        try:
            self.env["file_peinfo_FileDescription"] = pe_info_dict[
                "FileDescription"
            ].strip()
        except KeyError:
            self.output("Info: Missing FileDescription")
            self.env["file_peinfo_FileDescription"] = ""

        try:
            self.env["file_peinfo_InternalName"] = pe_info_dict["InternalName"].strip()
        except KeyError:
            self.output("Info: Missing InternalName")
            self.env["file_peinfo_InternalName"] = ""

        try:
            self.env["file_peinfo_OriginalFilename"] = pe_info_dict[
                "OriginalFilename"
            ].strip()
        except KeyError:
            self.output("Info: Missing OriginalFilename")
            self.env["file_peinfo_OriginalFilename"] = ""

        try:
            self.env["file_peinfo_LegalCopyright"] = pe_info_dict[
                "LegalCopyright"
            ].strip()
        except KeyError:
            self.output("Info: Missing LegalCopyright")
            self.env["file_peinfo_LegalCopyright"] = ""


if __name__ == "__main__":
    PROCESSOR = FileExeGetInfoPE()
    PROCESSOR.execute_shell()
