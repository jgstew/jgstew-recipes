#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/VersionMaximumArray.py
#
"""See docstring for VersionSort class"""

import looseversion
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["VersionSort"]


class VersionSort(Processor):  # pylint: disable=invalid-name
    """Sorts an array of version strings using version-aware comparison (so 1.2.10 sorts after 1.2.9)."""

    description = __doc__
    input_variables = {
        "version_array": {
            "required": False,
            "description": "Array of version strings to sort. Defaults to %match%.",
        },
        "sort_descending": {
            "required": False,
            "default": False,
            "description": "If True, sort newest-to-oldest. Default: False (oldest first)",
        },
    }
    output_variables = {
        "version_array_sorted": {
            "description": "The version array sorted in version order",
        },
        "version_maximum": {"description": "The newest (largest) version in the array"},
        "version_minimum": {
            "description": "The oldest (smallest) version in the array"
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        # Get `version_array` else `match`
        version_array = self.env.get("version_array", self.env.get("match"))
        sort_descending = bool(self.env.get("sort_descending", False))

        # Running Process
        if not version_array:
            raise ProcessorError("version_array is empty or not provided")

        # ascending order using version-aware comparison:
        ascending = sorted(version_array, key=looseversion.LooseVersion)

        # Writing output_variables
        self.env["version_minimum"] = ascending[0]
        self.env["version_maximum"] = ascending[-1]
        self.env["version_array_sorted"] = (
            list(reversed(ascending)) if sort_descending else ascending
        )

        self.output(
            f"Sorted {len(version_array)} versions: "
            f"min={self.env['version_minimum']}, max={self.env['version_maximum']}"
        )
        self.output(f"sorted: {self.env['version_array_sorted']}", 2)


if __name__ == "__main__":
    PROCESSOR = VersionSort()
    PROCESSOR.execute_shell()
