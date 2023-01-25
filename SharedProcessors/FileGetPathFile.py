#!/usr/local/autopkg/python
"""
See docstring for FileGetPathFile class
"""

import os
import shutil

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileGetPathFile"]


class FileGetPathFile(Processor):  # pylint: disable=too-few-public-methods
    """Gets the first executable in the list."""

    description = __doc__
    input_variables = {
        "command_name": {
            "required": True,
            "description": "name of the command to attempt to find on PATH",
        },
        "path_var_name": {
            "required": False,
            "default": "exe_path",
            "description": "name of the output variable to store the result",
        },
        "file_must_be_executable": {
            "required": False,
            "default": True,
            "description": "Does the file have to be executable?",
        },
    }
    output_variables = {
        "path_var_name": {"description": "the variable name to store output"},
        "path_result": {"description": "the result stored in the variable"},
    }

    def main(self):
        """execution starts here"""
        command_name = self.env.get("command_name", None)
        path_var_name = self.env.get("path_var_name", None)
        file_must_be_executable = self.env.get("file_must_be_executable", True)

        path = None

        # file must be executable by default
        mode = os.X_OK

        if not file_must_be_executable:
            mode = os.F_OK

        if command_name:
            path = shutil.which(command_name, mode)

        self.env[path_var_name] = path
        self.env["path_result"] = path


if __name__ == "__main__":
    PROCESSOR = FileGetPathFile()
    PROCESSOR.execute_shell()
