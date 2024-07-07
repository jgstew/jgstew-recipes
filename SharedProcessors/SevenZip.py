#!/usr/bin/python
"""Creates archive using the 7z utility.
"""
import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["SevenZip"]

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


class SevenZip(Processor):
    description = "Extracts the archive using 7z."
    input_variables = {
        "sevenzip_args": {
            "required": True,
            # "default": [],
            "description": "Array of cmd args to pass to 7z executable.",
        },
        "relative_directory": {
            "required": False,
            "default": False,
            "description": "relative directory.",
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
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        """Execution starts here:"""
        working_directory = self.env.get("RECIPE_CACHE_DIR")
        relative_directory = self.env.get("relative_directory", False)
        ignore_errors = self.env.get("ignore_errors", True)
        sevenzip_args = self.env.get("sevenzip_args", [])
        # verbosity = self.env.get("verbose", 0)

        # set initial default path:
        sevenzip = "7z"

        # find 7z executable in default paths:
        for exepath in [self.env.get("sevenzip_path", "")] + DEFAULT_7ZIP_PATHS:
            if os.path.isfile(exepath) and os.access(exepath, os.X_OK):
                sevenzip = exepath
                break

        self.output(f"Using Path to 7zip: {sevenzip}")

        # "-aoa" to always overwrite all files:
        cmd = [sevenzip] + sevenzip_args

        # if sevenzip_args and len(sevenzip_args) > 0:
        #     cmd.extend(sevenzip_args)

        self.output(f"7zip cmd line to be executed: {cmd}", 1)

        if relative_directory:
            os.chdir(os.path.join(working_directory, relative_directory))

        try:
            cmd_output = subprocess.check_output(cmd).decode("utf-8")
            self.output(f"Extraction Process Output: {cmd_output}", 2)
        except BaseException as err:
            self.output(f"ERROR: {err}", 2)
            if not ignore_errors:
                raise

        # reset working dir
        if relative_directory:
            os.chdir(working_directory)


if __name__ == "__main__":
    processor = SevenZip()
    processor.execute_shell()
