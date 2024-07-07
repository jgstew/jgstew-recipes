#!/usr/bin/python
"""
Created by James Stewart
Based on ExeVersionExtractor by Rusty Myers
Based on WinInstallerExtractor by Matt Hansen

Extracts version info from .exe file using the 7z utility.
"""

import os
import subprocess

from autopkglib import Processor, ProcessorError, is_windows
from SharedUtilityMethods import SharedUtilityMethods

__all__ = ["FileExeVersionExtractor"]

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


class FileExeVersionExtractor(SharedUtilityMethods):
    """Gets the EXE version from file."""

    description = __doc__
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
        },
        "ignore_errors": {
            "required": False,
            "default": True,
            "description": "Ignore any errors during the extraction.",
        },
        "sevenzip_path": {
            "required": False,
            "description": r"""
                Path to 7-Zip binary.
                Defaults to C:\Program Files\7-Zip\7z.exe on windows
                and Defaults to /usr/local/bin/7z on non-windows.
            """,
        },
        "version_string": {
            "required": False,
            "default": "ProductVersion:",
            "description": "The string to look for in file.",
        },
        "version_first": {
            "required": False,
            "default": False,
            "description": "If True, stop after first match.",
        },
    }
    output_variables = {
        "version": {"description": "Version of exe found."},
    }

    __doc__ = description

    def main(self):
        """Execution starts here"""
        exe_path = self.env.get("exe_path", self.env.get("pathname"))
        version_string = self.env.get("version_string", "ProductVersion:")
        version_first = self.verify_value_boolean(self.env.get("version_first", False))
        verbosity = self.env.get("verbose", 0)
        ignore_errors = self.env.get("ignore_errors", True)
        extract_flag = "l"

        self.verify_file_exists(exe_path)

        sevenzip_path = self.env.get("sevenzip_path", "/usr/local/bin/7z")

        # find 7z executable in default paths:
        for exepath in [sevenzip_path] + DEFAULT_7ZIP_PATHS:
            if os.path.isfile(exepath) and os.access(exepath, os.X_OK):
                sevenzip_path = exepath
                break

        self.output(f"Using 7z binary found here: {sevenzip_path}", 3)

        self.output("Extracting: %s" % exe_path)
        cmd = [sevenzip_path, extract_flag, "-y", exe_path]

        self.output(f"Command Line: {cmd}", 2)

        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)
        except BaseException:
            if ignore_errors != "True":
                raise

        self.output(f"Output: \n{Output}\n", 6)

        archiveVersion = ""
        # it is possible the encoding should only be treated as utf8
        #   if ascii option throws errors
        # https://stackoverflow.com/a/50627018/861745
        for line in Output.decode(encoding="utf8", errors="ignore").split("\n"):
            if verbosity > 2:
                print(line)
            if version_string in line:
                archiveVersion = line.split()[-1]
                if version_first:
                    break
                continue

        # for version numbers, this encode as ascii makes sense
        # for text, this might not make sense
        archive_version_ascii_only = archiveVersion.encode("ascii", "ignore").decode()
        self.env["version"] = archive_version_ascii_only
        self.output("Found Version: %s" % (self.env["version"]))


if __name__ == "__main__":
    processor = FileExeVersionExtractor()
    processor.execute_shell()
