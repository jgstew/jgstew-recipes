#!/usr/bin/python
"""Extracts the file using the 7z utility.
"""
import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["ExtractorSevenZip"]

DEFAULT_7ZIP_PATHS = [
    # Exe in current directory:
    "7z",
    "7z.exe",
    # MacOS typical:
    # NONINTERACTIVE=1 brew install p7zip
    "/opt/homebrew/bin/7z",
    "/usr/local/bin/7z",
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


class ExtractorSevenZip(Processor):
    description = "Extracts the archive using 7z."
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to file, defaults to %pathname%",
        },
        "preserve_paths": {
            "required": False,
            "default": True,
            "description": "eXtract archive with full paths, defaults to 'True'",
        },
        "extract_dir": {
            "required": False,
            "default": "tmp",
            "description": "Output path for the extracted archive.",
        },
        "ignore_pattern": {
            "required": False,
            "description": "Wildcard pattern to ignore files from the archive.",
        },
        "include_pattern": {
            "required": False,
            "description": "Wildcard pattern to include files from the archive.",
        },
        "ignore_errors": {
            "required": False,
            "default": True,
            "description": "Ignore any errors during the extraction.",
        },
        "sevenzip_path": {
            "required": False,
            "default": "",
            "description": "Path to 7-Zip binary.",
        },
        "sevenzip_args": {
            "required": False,
            "default": [],
            "description": "Array of cmd args to pass to 7z executable.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        """Execution starts here:"""
        file_path = self.env.get("file_path", self.env.get("pathname"))
        preserve_paths = self.env.get("preserve_paths", True)
        working_directory = self.env.get("RECIPE_CACHE_DIR")
        extract_directory = self.env.get("extract_dir", "tmp")
        ignore_pattern = self.env.get("ignore_pattern", "")
        include_pattern = self.env.get("include_pattern", "")
        ignore_errors = self.env.get("ignore_errors", True)
        sevenzip_args = self.env.get("sevenzip_args", [])
        # verbosity = self.env.get("verbose", 0)

        extract_flag = "x" if preserve_paths else "e"
        extract_path = f"{working_directory}/{extract_directory}"

        # set initial default path:
        sevenzip = "7z"

        # find 7z executable in default paths:
        for exepath in [self.env.get("sevenzip_path", "")] + DEFAULT_7ZIP_PATHS:
            if os.path.isfile(exepath) and os.access(exepath, os.X_OK):
                sevenzip = exepath
                break

        self.output(f"Using Path to 7zip: {sevenzip}")

        self.output(f"Extracting: {file_path}")
        cmd = [
            sevenzip,
            extract_flag,
            "-y",
            f"-o{extract_path}",
            file_path,
        ]

        # https://sevenzip.osdn.jp/chm/cmdline/switches/exclude.htm
        if ignore_pattern:
            cmd.append(f"-xr!{ignore_pattern}")

        # https://sevenzip.osdn.jp/chm/cmdline/switches/include.htm
        if include_pattern:
            cmd.append(f"-ir!{include_pattern}")

        if sevenzip_args and len(sevenzip_args) > 0:
            cmd.extend(sevenzip_args)

        self.output(f"7zip cmd line to be executed: {cmd}", 3)

        try:
            cmd_output = subprocess.check_output(cmd).decode("utf-8")
            self.output(f"Extraction Process Output: {cmd_output}", 4)
        except BaseException as err:
            self.output(f"ERROR: {err}", 2)
            if not ignore_errors:
                raise

        self.output(f"Extracted Archive Path: {extract_path}")


if __name__ == "__main__":
    processor = ExtractorSevenZip()
    processor.execute_shell()
