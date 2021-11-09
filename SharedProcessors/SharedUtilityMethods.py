#!/usr/bin/python
"""
Created by James Stewart

Does nothing on it's own

Contains Shared Class Method Utility Functions
"""

import errno
import os

from autopkglib import Processor, ProcessorError

__all__ = ["SharedUtilityMethods"]


class SharedUtilityMethods(Processor):
    """Provides shared class methods."""

    input_variables = {}
    output_variables = {}

    def verify_file_exists(self, file_path, raise_error=True):
        """verify file exists, raise error if not"""
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
        """verify file exists, raise error if not"""
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
        """load config info from file"""
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
        """Execution starts here"""
        self.output("WARNING: main() Does Nothing.", 4)


if __name__ == "__main__":
    print("SharedUtilityMethods: Does Nothing!")
