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
    """Gets the property the MSI file."""

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
        """read property from msi file"""
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
        """execution starts here"""
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
