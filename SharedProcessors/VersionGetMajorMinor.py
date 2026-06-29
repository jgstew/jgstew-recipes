#!/usr/local/autopkg/python
"""
See docstring for VersionGetMajorMinor class
"""

import looseversion
from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["VersionGetMajorMinor"]


def get_version_major_minor(vstring, separator_string="."):
    """Extract major and minor version components from a version string.

    Args:
        vstring: Version string to parse (e.g., '1.2.3.4')
        separator_string: Character(s) to insert between major and minor (default: '.')

    Returns:
        String containing only the major and minor parts joined by separator_string
    """
    lver = looseversion.LooseVersion(vstring)
    # NOTE: this should be done by using `packaging.version.parse` instead
    rval = separator_string.join([str(x) for x in lver.version[0:2]])
    return rval


class VersionGetMajorMinor(Processor):  # pylint: disable=too-few-public-methods
    """Extracts the major and minor version components from a version string with a configurable separator."""

    description = __doc__
    input_variables = {
        "version_string": {
            "required": False,
            "description": (
                "Version string to extract major.minor from. Defaults to %version_maximum%."
            ),
        },
        "separator_string": {
            "required": False,
            "default": ".",
            "description": ("string to separate the major.minor Defaults to '.'"),
        },
    }
    output_variables = {
        "version_major_minor": {"description": "The major.minor from the version."},
    }

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        # Get `version_string` else `version_maximum`
        version_string = self.env.get("version_string", self.env.get("version_maximum"))
        separator_string = self.env.get("separator_string", ".")

        # Running Process
        version_major_minor = get_version_major_minor(version_string, separator_string)

        # Writing output_variables
        self.env["version_major_minor"] = version_major_minor


if __name__ == "__main__":
    PROCESSOR = VersionGetMajorMinor()
    PROCESSOR.execute_shell()
