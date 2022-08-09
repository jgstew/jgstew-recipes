#!/usr/local/autopkg/python
"""
See docstring for FileMsiGetProperty class
"""

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
    }
    output_variables = {
        "file_msiinfo_ProductVersion": {"description": "ProductVersion"},
    }

    def get_property_msi(self, path, msi_property):
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

    def get_property_msilib(self):
        """for windows"""
        msi_path = self.env.get("msi_path", self.env.get("pathname", None))

        self.env["file_msiinfo_ProductVersion"] = self.get_property_msi(
            msi_path, "ProductVersion"
        )

    def main(self):
        """execution starts here"""
        msi_path = self.env.get("msi_path", self.env.get("pathname", None))
        self.output(msi_path)

        if msilib:
            self.output("Info: `msilib` found! Must be running on Windows.", 3)
            self.get_property_msilib()
        else:
            self.output(
                "Info: `msilib` not found, assuming non-Windows. Attempting to use `msiinfo` instead.",
                3,
            )

        self.output("TODO: implement!", 0)


if __name__ == "__main__":
    PROCESSOR = FileMsiGetProperty()
    PROCESSOR.execute_shell()
