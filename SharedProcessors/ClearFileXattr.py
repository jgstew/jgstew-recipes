#!/usr/local/autopkg/python
"""
Clear the etag xattr from file

Resolves:
- https://github.com/jgstew/jgstew-recipes/issues/3
"""

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
    xattr,
)
from SharedUtilityMethods import SharedUtilityMethods

__all__ = ["ClearFileXattr"]


class ClearFileXattr(SharedUtilityMethods):  # pylint: disable=invalid-name
    """Removes a specified extended attribute from a file, typically used to clear the etag and force a fresh download."""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": False,
            "description": ("Path to clear etag xattr. Defaults to %pathname%."),
        },
        "file_xattr": {
            "required": False,
            "default": "com.github.autopkg.etag",
            "description": "xattr to clear",
        },
    }
    output_variables = {"None": {}}

    __doc__ = description

    def clear_etag(self, file_path, file_xattr):
        """Remove a specified extended attribute from a file.

        Args:
            file_path: Path to the file to clear the attribute from
            file_xattr: Name of the extended attribute to remove

        Raises:
            OSError: Silently caught if the attribute does not exist
        """
        try:
            xattr.removexattr(file_path, file_xattr)
        except OSError:
            self.output("WARNING: Xattr not found", 1)

    def main(self):
        """Execution starts here."""

        # I think this gets the pathname value if `file_path` is not specified?
        file_path = self.env.get("file_path", self.env.get("pathname"))
        self.verify_file_exists(file_path)
        file_xattr = self.env.get("file_xattr", "com.github.autopkg.etag")

        self.clear_etag(file_path, file_xattr)


if __name__ == "__main__":
    PROCESSOR = ClearFileXattr()
    PROCESSOR.execute_shell()
