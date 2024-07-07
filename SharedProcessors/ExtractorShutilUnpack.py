#!/usr/bin/python
"""Extracts the file using shutil unpack_archive.

For more advanced extraction with 7zip, see:
- SharedProcessors/ExtractorSevenZip.py
"""
import os
import shutil
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["ExtractorShutilUnpack"]

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

DEFAULT_7ZIP_FORMATS = [
    ".7z",
    ".exe",
    ".rar",
    ".cab",
    ".iso",
    ".rpm",
    ".deb",
    ".wim",
    # alternatives exist for dmgs on MacOS:
    ".dmg",
]


class ExtractorShutilUnpack(Processor):
    """This processor unpacks an archive using shutil.unpack_archive"""

    description = "Extracts the archive using 7z."
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to file, defaults to %pathname%",
        },
        "file_format": {
            "required": False,
            "description": """The format of the archive
             (e.g. 'zip', 'tar', 'gztar', 'bztar', 'xztar', or '7z').
             If not specified, shutil will attempt to guess based on the file extension.
            """,
        },
        "extract_dir": {
            "required": False,
            "default": "tmp",
            "description": "Output path for the extracted archive.",
        },
        "ignore_errors": {
            "required": False,
            "default": True,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {}

    __doc__ = description

    def extract_7zip(self, filename, extract_dir):
        """Extracts 7zip archive using subprocess call to 7z."""

        # set initial default path:
        sevenzip = shutil.which("7z")

        if not sevenzip:
            sevenzip = ""

        # find 7z executable in default paths:
        for exepath in [sevenzip] + DEFAULT_7ZIP_PATHS:
            if os.path.isfile(exepath) and os.access(exepath, os.X_OK):
                sevenzip = exepath
                break

        if not sevenzip:
            raise ProcessorError(
                f"ERROR: 7zip executable not found! Needed to extract `{filename}`"
            )

        try:
            cmd_out = subprocess.check_output(
                [sevenzip, "x", "-y", "-o" + extract_dir, filename]
            )
            self.output(f"7zip subprocess output: {cmd_out}", 4)
        except subprocess.CalledProcessError as err:
            raise ProcessorError(
                f"Error extracting 7zip archive '{filename}': {err}"
            ) from err

    def main(self):
        """Execution starts here:"""
        file_path = self.env.get("file_path", self.env.get("pathname"))
        file_format = self.env.get("file_format", None)
        working_directory = self.env.get("RECIPE_CACHE_DIR")
        extract_directory = self.env.get("extract_dir", "tmp")
        ignore_errors = self.env.get("ignore_errors", True)
        # verbosity = self.env.get("verbose", 0)

        extract_path = f"{working_directory}/{extract_directory}"

        # Register 7zip format with shutil
        shutil.register_unpack_format(
            "7zip",
            DEFAULT_7ZIP_FORMATS,
            self.extract_7zip,
            description="Uses 7z executable to extract many extra formats",
        )

        self.output(f"Supported formats: {shutil.get_unpack_formats()}", 4)

        try:
            if file_format:
                shutil.unpack_archive(file_path, extract_path, file_format)
            else:
                shutil.unpack_archive(file_path, extract_path)

            self.output(f"Extracted Archive Path: {extract_path}")
        except BaseException as err:
            err_message = f"ERROR extracting archive '{file_path}': {err}"
            if not ignore_errors:
                raise ProcessorError(err_message) from err

            # if 7z not found, raise error anyway:
            if "7zip executable not found!" in err_message:
                raise ProcessorError(err_message) from err
            self.output(err_message, 2)


if __name__ == "__main__":
    processor = ExtractorShutilUnpack()
    processor.execute_shell()
