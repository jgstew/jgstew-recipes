#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/ExtractorSevenZip.py
#
"""See docstring for FileArchiveListContents class"""

import os
import subprocess

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileArchiveListContents"]

DEFAULT_7ZIP_PATHS = [
    # Exe in current directory:
    "7z",
    "7z.exe",
    # MacOS typical:
    # NONINTERACTIVE=1 brew install p7zip
    "/opt/homebrew/bin/7z",
    "/usr/local/bin/7z",
    "/opt/homebrew/bin/7zz",
    # NONINTERACTIVE=1 brew install sevenzip
    "/usr/local/bin/7zz",
    # Ubuntu typical:
    # sudo apt-get install -y p7zip-full
    "/usr/bin/7z",
    # Windows typical:
    # choco install -y 7zip
    "/Program Files/7-Zip/7z.exe",
    "/Program Files (x86)/7-Zip/7z.exe",
]


class FileArchiveListContents(Processor):  # pylint: disable=invalid-name
    """Lists the contents of an archive (zip/7z/tar/etc.) without extracting it, using the 7z executable."""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to the archive file, defaults to %pathname%",
        },
        "sevenzip_path": {
            "required": False,
            "default": "",
            "description": "Path to 7-Zip binary. Defaults to searching common locations.",
        },
    }
    output_variables = {
        "archive_contents": {
            "description": "Array of file/folder paths contained in the archive",
        },
        "archive_file_count": {
            "description": "Number of entries found in the archive",
        },
    }
    __doc__ = description

    def find_sevenzip(self):
        """Locate the 7z executable from the configured or default paths.

        Returns:
            Path to the first 7z executable found, or '7z' as a fallback
        """
        for exepath in [self.env.get("sevenzip_path", "")] + DEFAULT_7ZIP_PATHS:
            if exepath and os.path.isfile(exepath) and os.access(exepath, os.X_OK):
                return exepath
        return "7z"

    def main(self):
        """Execution starts here."""
        file_path = self.env.get("file_path", self.env.get("pathname"))

        if not file_path or not os.path.isfile(file_path):
            raise ProcessorError(f"Archive file not found: {file_path}")

        sevenzip = self.find_sevenzip()
        self.output(f"Using Path to 7zip: {sevenzip}")

        # `l -slt` produces a technical listing with one `Path = ...` line per entry.
        cmd = [sevenzip, "l", "-slt", file_path]
        self.output(f"7zip cmd line to be executed: {cmd}", 3)

        try:
            cmd_output = subprocess.check_output(cmd).decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as err:
            raise ProcessorError(f"Failed to list archive contents: {err}") from err

        # In `-slt` output the archive's own path appears in the header before the
        # `----------` separator; entries are listed after it.
        listing = cmd_output.split("----------", 1)
        entries_text = listing[1] if len(listing) > 1 else cmd_output

        archive_contents = [
            line.split("=", 1)[1].strip()
            for line in entries_text.splitlines()
            if line.startswith("Path = ")
        ]

        self.output(f"Archive contains {len(archive_contents)} entries")
        self.output(archive_contents, 3)

        self.env["archive_contents"] = archive_contents
        self.env["archive_file_count"] = len(archive_contents)


if __name__ == "__main__":
    PROCESSOR = FileArchiveListContents()
    PROCESSOR.execute_shell()
