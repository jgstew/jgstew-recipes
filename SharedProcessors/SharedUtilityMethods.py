#!/usr/bin/python
"""
Created by James Stewart

Does nothing on it's own

Contains Shared Class Method Utility Functions
"""

import errno
import os
import shutil

from autopkglib import Processor, ProcessorError

# __all__ declares this module's public API: the names bound by
# `from SharedUtilityMethods import *`, and the supported, intentional imports
# for other processors. Besides the SharedUtilityMethods processor class, the
# shared executable-finder helpers and their default path lists are listed here
# so sibling processors can import them directly (e.g. `from SharedUtilityMethods
# import find_7zip`) instead of each carrying its own copy.
__all__ = [
    "SharedUtilityMethods",
    "DEFAULT_7ZIP_PATHS",
    "DEFAULT_FFMPEG_PATHS",
    "find_executable",
    "find_7zip",
    "find_ffmpeg",
]

# Common install locations for the 7-Zip CLI, searched in order.
#   MacOS:   brew install p7zip   (or `sevenzip` for the 7zz binary)
#   Ubuntu:  sudo apt-get install -y p7zip-full
#   Windows: choco install -y 7zip
DEFAULT_7ZIP_PATHS = [
    "7z",
    "7z.exe",
    "/opt/homebrew/bin/7z",
    "/usr/local/bin/7z",
    "/opt/homebrew/bin/7zz",
    "/usr/local/bin/7zz",
    "/usr/bin/7z",
    "/Program Files/7-Zip/7z.exe",
    "/Program Files (x86)/7-Zip/7z.exe",
]

# Common install locations for the ffmpeg CLI, searched in order.
#   MacOS:   brew install ffmpeg
#   Ubuntu:  sudo apt-get install -y ffmpeg
#   Windows: choco install -y ffmpeg
DEFAULT_FFMPEG_PATHS = [
    "ffmpeg",
    "ffmpeg.exe",
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/usr/bin/ffmpeg",
    "/Program Files/ffmpeg/bin/ffmpeg.exe",
    "/ProgramData/chocolatey/bin/ffmpeg.exe",
]


def find_executable(path_array, default=None):
    """Return the first path in path_array that is an executable file.

    If none of the candidates exist and a default is provided, fall back to
    looking the default up on the system PATH (via shutil.which) - this resolves
    a command name like "7z" that is installed in a location not listed in
    path_array. If it is not on PATH either, the default value is returned as-is.

    Args:
        path_array: Ordered list of candidate executable paths.
        default: Value to return if no candidate is found; also looked up on the
            PATH when it is a command name (default: None).

    Returns:
        The first existing executable path; otherwise the default resolved on the
        PATH; otherwise the default value unchanged.
    """
    for exe_path in path_array:
        if exe_path and os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
    if default:
        return shutil.which(default) or default
    return default


def find_7zip(sevenzip_path=""):
    """Locate the 7z executable, trying sevenzip_path then common locations.

    Args:
        sevenzip_path: Optional explicit path to try first.

    Returns:
        Path to the first 7z executable found, or "7z" as a fallback.
    """
    return find_executable([sevenzip_path] + DEFAULT_7ZIP_PATHS, default="7z")


def find_ffmpeg(ffmpeg_path=""):
    """Locate the ffmpeg executable, trying ffmpeg_path then common locations.

    Args:
        ffmpeg_path: Optional explicit path to try first.

    Returns:
        Path to the first ffmpeg executable found, or "ffmpeg" as a fallback.
    """
    return find_executable([ffmpeg_path] + DEFAULT_FFMPEG_PATHS, default="ffmpeg")


class SharedUtilityMethods(Processor):
    """Base processor class providing shared utility methods for file verification, executable checking, and BigFix configuration loading."""

    input_variables = {}
    output_variables = {}

    def verify_file_exists(self, file_path, raise_error=True):
        """Verify that a file exists at the given path.

        Args:
            file_path: Path to verify
            raise_error: If True, raise an error when the file is missing (default: True)

        Returns:
            file_path if the file exists, None otherwise

        Raises:
            ProcessorError or FileNotFoundError if raise_error is True and the file is not found
        """
        verbosity = 3
        if raise_error:
            verbosity = 0
        if not file_path:
            self.output("ERROR: no file_path provided!", verbosity)
            if raise_error:
                raise ProcessorError("No file_path provided!")
        elif not os.path.isfile(file_path):
            self.output(f"ERROR: file missing! `{file_path}`", verbosity)
            if raise_error:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), file_path
                )
            return None
        return file_path

    def verify_folder_exists(self, folder_path, raise_error=True):
        """Verify that a folder exists at the given path.

        Args:
            folder_path: Path to verify
            raise_error: If True, raise an error when the folder is missing (default: True)

        Returns:
            folder_path if the folder exists, None otherwise

        Raises:
            ProcessorError or FileNotFoundError if raise_error is True and the folder is not found
        """
        verbosity = 3
        if raise_error:
            verbosity = 0
        if not folder_path:
            self.output("ERROR: no folder_path provided!", verbosity)
            if raise_error:
                raise ProcessorError("No file_path provided!")
        elif not os.path.isdir(folder_path):
            self.output(f"ERROR: folder missing! `{folder_path}`", verbosity)
            if raise_error:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), folder_path
                )
            return None
        return folder_path

    def verify_file_executable(self, file_path, raise_error=False):
        """verify file is executable"""
        file_path_exists = self.verify_file_exists(file_path, raise_error)

        if file_path_exists and os.access(file_path_exists, os.X_OK):
            return True

        return False

    def verify_value_boolean(self, value, raise_error=True):
        """verify value is boolean"""
        if not isinstance(value, bool):
            self.output(f"ERROR: value not boolean `{value}`", 0)
            if raise_error:
                raise TypeError(f"Must be boolean! `{value}`")
        return value

    def get_config(self, conf_file=None):
        """Load BigFix/besapi connection configuration from standard config file locations.

        Searches /etc/besapi.conf, ~/besapi.conf, ~/.besapi.conf, besapi.conf, and an optional
        custom path, setting BES_ROOT_SERVER, BES_USER_NAME, and BES_PASSWORD in the environment.

        Args:
            conf_file: Optional path to an additional config file to search
        """
        # this is from BESImport.py

        try:
            from ConfigParser import SafeConfigParser
        except (ImportError, ModuleNotFoundError):
            from configparser import SafeConfigParser

        config_path = [
            "/etc/besapi.conf",
            os.path.expanduser("~/besapi.conf"),
            os.path.expanduser("~/.besapi.conf"),
            "besapi.conf",
        ]
        if conf_file:
            config_path.append(conf_file)

        CONFPARSER = SafeConfigParser()
        CONFPARSER.read(config_path)

        if CONFPARSER:
            try:
                self.env["BES_ROOT_SERVER"] = CONFPARSER.get(
                    "besapi", "BES_ROOT_SERVER"
                )
                self.env["BES_USER_NAME"] = CONFPARSER.get("besapi", "BES_USER_NAME")
                self.env["BES_PASSWORD"] = CONFPARSER.get("besapi", "BES_PASSWORD")
            except KeyError as err:
                self.output(err, 0)
                self.env["stop_processing_recipe"] = True
                raise

    def main(self):
        """Execution starts here."""
        self.output("WARNING: main() Does Nothing.", 4)


if __name__ == "__main__":
    print("SharedUtilityMethods: Does Nothing!")
