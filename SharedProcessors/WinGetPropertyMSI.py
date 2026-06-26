#!/usr/local/autopkg/python
"""
See docstring for WinGetPropertyMSI class
"""

try:
    import msilib
except ImportError:
    print("ImportError: msilib")
    print("  Note: this is expected on non-windows platforms")


from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
    is_windows,
)

__all__ = ["WinGetPropertyMSI"]


class WinGetPropertyMSI(Processor):  # pylint: disable=too-few-public-methods
    """Reads a property from an MSI file using Windows msilib. Windows-only; use FileMsiGetProperty for cross-platform support."""

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
        self.output(
            "INFO: Consider using the new and improved `FileMsiGetProperty` processor instead!"
        )

        if not msilib:
            self.output("WARNING: This does not work on non-Windows", 0)
            return ""

        msi_filepath = self.env.get("pathname", None)
        msi_property = self.env.get("msi_property", None)
        msi_property_value = self.get_property_msi(msi_filepath, msi_property)

        self.output(msi_property_value, 2)

        self.env["msi_property_value"] = msi_property_value

        if " " not in msi_property:
            self.env[msi_property] = msi_property_value

        return msi_property_value


if __name__ == "__main__":
    PROCESSOR = WinGetPropertyMSI()
    PROCESSOR.execute_shell()
