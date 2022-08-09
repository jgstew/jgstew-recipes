#!/usr/local/autopkg/python
"""
See docstring for FileMsiGetProperty class
"""

import errno
import os

try:
    import msilib
except ImportError:
    # this is expected on non-windows!
    pass

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileMsiGetProperty"]


class FileMsiGetProperty(Processor):  # pylint: disable=too-few-public-methods
    """Get properties from MSI files using 2 different methods.

    Use `msilib` on Windows
    Use `msiinfo` binary on non-Windows
    - Ubuntu: sudo apt-get install msitools -y
    - MacOS:  brew install msitools

    See predecessors:
    - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/WinGetPropertyMSI.py
    - https://github.com/autopkg/hansen-m-recipes/blob/master/SharedProcessors/MSIInfoVersionProvider.py
    - https://github.com/autopkg/hansen-m-recipes/blob/master/SharedProcessors/MSIVersionProvider.py
    """

    description = __doc__
    input_variables = {
        "msi_path": {
            "required": False,
            "description": "Path to the .msi, defaults to %pathname%",
        },
        # default to `/usr/bin/msiinfo` or `?`
        "msiinfo_path": {
            "required": False,
            "description": "Path to the msiinfo binary. Not used on Windows.",
        },
        "custom_msi_property": {
            "required": False,
            "default": "ProductVersion",
            "description": "Custom index to retrieve, defaults to `author`",
        },
        "custom_msi_output": {
            "required": False,
            "default": "version",
            "description": "Variable to store the output to, defaults to `file_ole_author`",
        },
    }
    output_variables = {
        "file_msiinfo_ProductVersion": {"description": "ProductVersion"},
    }

    def get_property_msi_msilib(self, path, msi_property):
        """read property from msi file"""
        # https://stackoverflow.com/a/9768876/861745
        msi_db = msilib.OpenDatabase(path, msilib.MSIDBOPEN_READONLY)
        view = msi_db.OpenView(
            "SELECT Value FROM Property WHERE Property='" + msi_property + "'"
        )
        view.Execute(None)
        result = view.Fetch()
        # self.output(dir(result), 3)
        return result.GetString(1)

    def get_properties_msilib(self):
        """for windows"""
        msi_path = self.env.get("msi_path", self.env.get("pathname", None))
        custom_msi_property = self.env.get("custom_msi_property", None)
        custom_msi_output = self.env.get("custom_msi_output", None)

        self.env["file_msiinfo_ProductVersion"] = self.get_property_msi_msilib(
            msi_path, "ProductVersion"
        )

        self.env[custom_msi_output] = self.get_property_msi_msilib(
            msi_path, custom_msi_property
        )

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

    def verify_file_executable(self, file_path, raise_error=False):
        """verify file is executable"""
        file_path_exists = self.verify_file_exists(file_path, raise_error)

        if file_path_exists and os.access(file_path_exists, os.X_OK):
            return True

        return False

    def get_msiinfo_path(self):
        msiinfo_path_input = self.env.get("msiinfo_path", None)
        msiinfo_path = None

        path_array = ["/usr/bin/msiinfo", "/usr/local/bin/msiinfo"]
        if msiinfo_path_input:
            path_array.append(msiinfo_path_input)
            # put provided path first
            path_array.reverse()

        for path in path_array:
            if self.verify_file_executable(path):
                msiinfo_path = path
                break

        return msiinfo_path

    def get_properties_msiinfo(self):
        """for non-windows

        based upon:
        - https://github.com/autopkg/hansen-m-recipes/blob/master/SharedProcessors/MSIInfoVersionProvider.py
        """
        # msi_path = self.env.get("msi_path", self.env.get("pathname", None))
        # custom_msi_property = self.env.get("custom_msi_property", None)
        # custom_msi_output = self.env.get("custom_msi_output", None)

        msiinfo_path = self.get_msiinfo_path()

        if not msiinfo_path:
            raise ProcessorError(
                """
                msiinfo binary not found!
                Install on MacOS with `brew install msitools`
                Install on Ubuntu with `sudo apt-get install msitools -y`
                """
            )

        self.output(msiinfo_path)

    def main(self):
        """execution starts here"""
        msi_path = self.env.get("msi_path", self.env.get("pathname", None))
        self.verify_file_exists(msi_path)
        self.output(msi_path)

        if msilib:
            self.output("Info: `msilib` found! Must be running on Windows.", 3)
            self.get_properties_msilib()
        else:
            self.output(
                "Info: `msilib` not found, assuming non-Windows. Attempting to use `msiinfo` instead.",
                3,
            )
            self.get_properties_msiinfo()

        self.output("TODO: implement on non-windows!", 0)


if __name__ == "__main__":
    PROCESSOR = FileMsiGetProperty()
    PROCESSOR.execute_shell()
