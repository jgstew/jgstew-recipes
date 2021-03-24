#!/usr/local/autopkg/python
"""
Clear the etag xattr from file

Resolves:
- https://github.com/jgstew/jgstew-recipes/issues/3
"""

from autopkglib import Processor, ProcessorError, xattr  # pylint: disable=import-error,unused-import

__all__ = ["ClearFileXattr"]


class ClearFileXattr(Processor):  # pylint: disable=invalid-name
    """Clear the etag xattr from file"""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": False,
            "description": (
                "Path to clear etag xattr. Defaults to %pathname%."
            ),
        },
        "file_xattr": {
            "required": False,
            "default": "com.github.autopkg.etag",
            "description": "xattr to clear",
        }
    }
    output_variables = {
        "None": {
            
        }
    }

    __doc__ = description

    def clear_etag(self, file_path, file_xattr):
        """
        clear xattr from file

        Keyword arguments:
        file_path -- the file to clear
        """
        try:
            xattr.removexattr(file_path, file_xattr)
        except OSError:
            self.output("WARNING: Xattr not found", 1)

    def main(self):
        """Execution starts here"""

        # I think this gets the pathname value if `file_path` is not specified?
        file_path = self.env.get("file_path", self.env.get("pathname"))
        file_xattr = self.env.get("file_xattr", "com.github.autopkg.etag")

        self.clear_etag(file_path, file_xattr)


if __name__ == "__main__":
    PROCESSOR = ClearFileXattr()
    PROCESSOR.execute_shell()
