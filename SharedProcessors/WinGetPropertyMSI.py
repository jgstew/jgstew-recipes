#!/usr/local/autopkg/python
"""
See docstring for WinGetPropertyMSI class
"""

import os
import warnings

try:
    import msilib
except ImportError:
    # msilib is Windows-only; define it as None so the non-Windows path in
    # main() can detect its absence instead of raising a NameError.
    msilib = None
    print("ImportError: msilib")
    print("  Note: this is expected on non-windows platforms")


from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
    is_windows,
)

__all__ = ["WinGetPropertyMSI"]

DEPRECATION_MESSAGE = (
    "WinGetPropertyMSI is deprecated and will be removed in a future release. "
    "Use the cross-platform FileMsiGetProperty processor instead, which works on Windows, macOS, and "
    "Linux."
)


class WinGetPropertyMSI(Processor):  # pylint: disable=too-few-public-methods
    f"""DEPRECATED: Reads a property from an MSI file using Windows only msilib.

    {DEPRECATION_MESSAGE}
    """

    description = __doc__
    input_variables = {
        "pathname": {
            "required": True,
            "description": "pathname to MSI file to read msi_property from",
        },
        "msi_property": {
            "required": False,
            "default": "ProductVersion",
            "description": (
                "Name of the property to read from the Property table."
                " Defaults to 'ProductVersion'"
            ),
        },
    }
    output_variables = {
        "msi_property_value": {
            "description": "The value of the property if applicable."
        },
        "deprecation_warning": {
            "description": "The deprecation warning message emitted by this processor."
        },
    }

    def get_property_msi(self, path, msi_property):
        """Read a property value from a Windows MSI database using msilib.

        Args:
            path: Path to the MSI file
            msi_property: Name of the property to retrieve (e.g., 'ProductVersion')

        Returns:
            Property value as a string

        Raises:
            Exception: If the property is not found or the MSI query fails
        """
        # https://stackoverflow.com/a/9768876/861745
        msi_db = msilib.OpenDatabase(path, msilib.MSIDBOPEN_READONLY)
        view = msi_db.OpenView(
            "SELECT Value FROM Property WHERE Property='" + msi_property + "'"
        )
        view.Execute(None)
        result = view.Fetch()
        self.output(dir(result), 3)
        return result.GetString(1)

    def main(self):
        """Execution starts here."""
        # emit a real DeprecationWarning for tooling/log capture:
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        # always-visible warning in AutoPkg output (verbosity 0):
        self.output(f"DEPRECATION WARNING: {DEPRECATION_MESSAGE}", 0)
        # expose the warning as an output variable so it can be asserted on:
        self.env["deprecation_warning"] = DEPRECATION_MESSAGE

        if not msilib:
            self.output("WARNING: This does not work on non-Windows", 0)
            return ""

        msi_filepath = self.env.get("pathname", None)
        msi_property = self.env.get("msi_property", None)

        # gracefully skip the read if the MSI is missing (keeps this cross-platform
        # safe to invoke, e.g. for the deprecation-only test recipe):
        if not msi_filepath or not os.path.isfile(msi_filepath):
            self.output(
                f"WARNING: MSI file not found, skipping read: {msi_filepath}", 0
            )
            return ""

        msi_property_value = self.get_property_msi(msi_filepath, msi_property)

        self.output(msi_property_value, 2)

        self.env["msi_property_value"] = msi_property_value

        if " " not in msi_property:
            self.env[msi_property] = msi_property_value

        return msi_property_value


if __name__ == "__main__":
    PROCESSOR = WinGetPropertyMSI()
    PROCESSOR.execute_shell()
