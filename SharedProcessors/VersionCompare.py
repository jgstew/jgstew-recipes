#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/VersionGetMajorMinor.py
#
"""See docstring for VersionCompare class"""

import looseversion
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["VersionCompare"]


def compare_versions(version1, version2):
    """Compare two version strings.

    Args:
        version1: First version string (e.g. '1.2.3')
        version2: Second version string (e.g. '1.2.10')

    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    lver1 = looseversion.LooseVersion(str(version1))
    lver2 = looseversion.LooseVersion(str(version2))
    if lver1 < lver2:
        return -1
    if lver1 > lver2:
        return 1
    return 0


class VersionCompare(Processor):  # pylint: disable=invalid-name
    """Compares two version strings and reports whether the first is newer, older, or equal to the second."""

    description = __doc__
    input_variables = {
        "version1": {
            "required": True,
            "description": "First version string to compare",
        },
        "version2": {
            "required": True,
            "description": "Second version string to compare against",
        },
    }
    output_variables = {
        "version_comparison_result": {
            "description": (
                "'newer', 'older', or 'equal' describing version1 relative to version2"
            ),
        },
        "version_comparison_int": {
            "description": "-1 if version1 < version2, 0 if equal, 1 if version1 > version2",
        },
        "version_newest": {
            "description": "The newer of the two version strings (version2 if equal)",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        version1 = self.env.get("version1")
        version2 = self.env.get("version2")

        # Running Process
        comparison_int = compare_versions(version1, version2)

        if comparison_int < 0:
            result = "older"
            newest = version2
        elif comparison_int > 0:
            result = "newer"
            newest = version1
        else:
            result = "equal"
            newest = version2

        self.output(f"`{version1}` is {result} than/to `{version2}`")

        # Writing output_variables
        self.env["version_comparison_result"] = result
        self.env["version_comparison_int"] = comparison_int
        self.env["version_newest"] = newest


if __name__ == "__main__":
    PROCESSOR = VersionCompare()
    PROCESSOR.execute_shell()
