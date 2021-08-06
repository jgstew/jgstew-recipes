#!/usr/local/autopkg/python
"""
See docstring for VersionMaximumArray class
"""

import distutils.version

from autopkglib import (
    Processor,
    ProcessorError,
)  # pylint: disable=import-error,unused-import


__all__ = ["VersionMaximumArray"]


class VersionMaximumArray(Processor):  # pylint: disable=too-few-public-methods
    """Gets the maximum version string from an array."""

    description = __doc__
    input_variables = {
        "version_array": {
            "required": False,
            "description": ("Array of Versions. Defaults to %match%."),
        }
    }
    output_variables = {
        "version_maximum": {"description": "The maximum version from the array."},
    }

    def main(self):
        """execution starts here"""

        # Get `version_array` else `match`
        version_array = self.env.get("version_array", self.env.get("match"))

        version_maximum = max(version_array, key=distutils.version.LooseVersion)

        # print(version_maximum)

        self.env["version_maximum"] = version_maximum


if __name__ == "__main__":
    PROCESSOR = VersionMaximumArray()
    PROCESSOR.execute_shell()
