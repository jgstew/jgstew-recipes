#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileExeGetInfoPE.py
#
"""See docstring for FileExeGetInfoPeExpanded class"""

import datetime

# pip install pefile
import pefile
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileExeGetInfoPeExpanded"]

# PE FILE_HEADER.Machine values -> friendly architecture names:
MACHINE_TYPES = {
    0x014C: "x86",
    0x8664: "x64",
    0x01C0: "arm",
    0xAA64: "arm64",
    0x0200: "ia64",
}

# PE OPTIONAL_HEADER.Subsystem values -> friendly names:
SUBSYSTEM_TYPES = {
    1: "native",
    2: "windows_gui",
    3: "windows_console",
}


class FileExeGetInfoPeExpanded(Processor):  # pylint: disable=invalid-name
    """Extracts structural PE info (compile timestamp, architecture, subsystem, sections, and imported DLLs) from a Windows PE file using pefile."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Windows PE file to inspect, defaults to %pathname%",
        },
    }
    output_variables = {
        "file_pe_compile_datetime": {
            "description": "PE compile timestamp as 'YYYY-MM-DD HH:MM:SS' (UTC)",
        },
        "file_pe_compile_date": {
            "description": "PE compile date as 'YYYY-MM-DD' (UTC)",
        },
        "file_pe_machine": {
            "description": "Target architecture: x86, x64, arm, arm64, ia64, or hex value",
        },
        "file_pe_subsystem": {
            "description": "Subsystem: native, windows_gui, windows_console, or numeric value",
        },
        "file_pe_is_dll": {"description": "True if the file is a DLL"},
        "file_pe_is_exe": {"description": "True if the file is an EXE"},
        "file_pe_sections": {
            "description": "Array of section names (e.g. .text, .data)"
        },
        "file_pe_imported_dlls": {"description": "Array of imported DLL names"},
        "file_pe_imported_dll_count": {"description": "Number of imported DLLs"},
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))

        if not file_pathname:
            raise ProcessorError("No file_pathname provided")

        try:
            pe = pefile.PE(file_pathname)
        except pefile.PEFormatError as err:
            raise ProcessorError(
                f"Not a valid PE file ({file_pathname}): {err}"
            ) from err

        # compile timestamp from the COFF file header:
        timestamp = pe.FILE_HEADER.TimeDateStamp
        compile_dt = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        self.env["file_pe_compile_datetime"] = compile_dt.strftime("%Y-%m-%d %H:%M:%S")
        self.env["file_pe_compile_date"] = compile_dt.strftime("%Y-%m-%d")

        # architecture and subsystem, mapped to friendly names when known:
        machine = pe.FILE_HEADER.Machine
        self.env["file_pe_machine"] = MACHINE_TYPES.get(machine, hex(machine))
        subsystem = pe.OPTIONAL_HEADER.Subsystem
        self.env["file_pe_subsystem"] = SUBSYSTEM_TYPES.get(subsystem, str(subsystem))

        self.env["file_pe_is_dll"] = pe.is_dll()
        self.env["file_pe_is_exe"] = pe.is_exe()

        # section names (trim trailing NUL padding):
        self.env["file_pe_sections"] = [
            section.Name.decode("utf-8", "replace").rstrip("\x00")
            for section in pe.sections
        ]

        # imported DLLs (only present if the file imports anything):
        imported_dlls = []
        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            imported_dlls = [
                entry.dll.decode("utf-8", "replace")
                for entry in pe.DIRECTORY_ENTRY_IMPORT
            ]
        self.env["file_pe_imported_dlls"] = imported_dlls
        self.env["file_pe_imported_dll_count"] = len(imported_dlls)

        self.output(
            f"PE {self.env['file_pe_machine']} "
            f"{self.env['file_pe_subsystem']} compiled {self.env['file_pe_compile_date']}, "
            f"{len(imported_dlls)} imported DLLs"
        )
        self.output(f"sections: {self.env['file_pe_sections']}", 2)
        self.output(f"imported DLLs: {imported_dlls}", 3)


if __name__ == "__main__":
    PROCESSOR = FileExeGetInfoPeExpanded()
    PROCESSOR.execute_shell()
