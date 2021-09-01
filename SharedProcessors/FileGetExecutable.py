#!/usr/local/autopkg/python
"""
See docstring for FileGetExecutable class
"""

import os

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileGetExecutable"]


class FileGetExecutable(Processor):  # pylint: disable=too-few-public-methods
    """Gets the first executable in the list."""

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
        """execution starts here"""
        path_array = self.env.get("path_array", None)
        path_var_name = self.env.get("path_var_name", None)

        for path in path_array:
            print(path)
            # if self.verify_file_executable(path):
            if os.path.isfile(path) and os.access(path, os.X_OK):
                self.env[path_var_name] = path
                self.env["path_result"] = path
                break


if __name__ == "__main__":
    PROCESSOR = FileGetExecutable()
    PROCESSOR.execute_shell()
