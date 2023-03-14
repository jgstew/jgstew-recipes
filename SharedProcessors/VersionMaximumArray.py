#!/usr/local/autopkg/python
"""
See docstring for VersionMaximumArray class
"""

import looseversion
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["VersionMaximumArray"]


class VersionMaximumArray(Processor):  # pylint: disable=too-few-public-methods
    """Gets the maximum version string from an array."""

    description = __doc__
    input_variables = {
        "version_array": {
            "required": False,
            "description": ("Array of Versions. Defaults to %match%."),
        },
        "version_major_minor_match": {
            "required": False,
            "default": "",
            "description": (
                "Major Minor version to filter matches. Defaults to empty string."
            ),
        },
    }
    output_variables = {
        "version_maximum": {"description": "The maximum version from the array."},
    }

    def main(self):
        """execution starts here"""

        # Get `version_array` else `match`
        version_array = self.env.get("version_array", self.env.get("match"))
        version_major_minor_match = self.env.get("version_major_minor_match", "")
        filtered_array = []

        # NOTE: this should be done by using `packaging.version.parse` instead
        if version_major_minor_match != "":
            if not version_major_minor_match.endswith("."):
                version_major_minor_match += "."
            for item in version_array:
                if item.startswith(version_major_minor_match):
                    filtered_array.append(item)
            version_array = filtered_array

        # get maximum version:
        version_maximum = max(version_array, key=looseversion.LooseVersion)

        self.env["version_maximum"] = version_maximum


if __name__ == "__main__":
    PROCESSOR = VersionMaximumArray()
    PROCESSOR.execute_shell()
