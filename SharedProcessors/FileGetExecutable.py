#!/usr/local/autopkg/python
"""
See docstring for FileGetExecutable class
"""

import os
import sys

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

# Add this processor's own directory to sys.path so the sibling SharedProcessors
# module below can be imported without requiring SharedUtilityMethods to run
# first in the recipe.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SharedUtilityMethods import SharedUtilityMethods  # noqa: E402  isort:skip

__all__ = ["FileGetExecutable"]


class FileGetExecutable(SharedUtilityMethods):  # pylint: disable=too-few-public-methods
    """Searches an ordered list of paths for the first executable file and stores its path in a named environment variable."""

    description = __doc__
    input_variables = {
        "path_array": {
            "required": True,
            "description": "array of paths to find first executable within",
        },
        "path_var_name": {
            "required": False,
            "default": "sevenzip_path",
            "description": "name of the output variable to store the result",
        },
    }
    output_variables = {
        "path_var_name": {"description": "the variable name to store output"},
        "path_result": {"description": "the result stored in the variable"},
    }

    def main(self):
        """Execution starts here."""
        path_array = self.env.get("path_array", None)
        path_var_name = self.env.get("path_var_name", None)

        for path in path_array:
            # if os.path.isfile(path) and os.access(path, os.X_OK):
            if self.verify_file_executable(path):
                self.env[path_var_name] = path
                self.env["path_result"] = path
                break


if __name__ == "__main__":
    PROCESSOR = FileGetExecutable()
    PROCESSOR.execute_shell()
