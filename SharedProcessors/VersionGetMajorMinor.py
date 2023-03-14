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
    """Return an X.Y version"""
    lver = looseversion.LooseVersion(vstring)
    # NOTE: this should be done by using `packaging.version.parse` instead
    rval = separator_string.join([str(x) for x in lver.version[0:2]])
    return rval


class VersionGetMajorMinor(Processor):  # pylint: disable=too-few-public-methods
    """Gets the major.minor string from the version."""

    description = __doc__
    input_variables = {
        "version_string": {
            "required": False,
            "description": ("Array of Versions. Defaults to %version_maximum%."),
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
        """execution starts here"""

        # Get `version_string` else `version_maximum`
        version_string = self.env.get("version_string", self.env.get("version_maximum"))
        separator_string = self.env.get("separator_string", ".")

        version_major_minor = get_version_major_minor(version_string, separator_string)

        self.env["version_major_minor"] = version_major_minor


if __name__ == "__main__":
    PROCESSOR = VersionGetMajorMinor()
    PROCESSOR.execute_shell()
