#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileTouch class"""

import pathlib

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileTouch"]


class FileTouch(Processor):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "pathname": {"required": True, "description": "file to update"},
        "touch_create_folders": {
            "required": False,
            "default": False,
            "description": "Create missing folders in path? Default: False",
        },
    }
    output_variables = {
        "touch_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        pathname = self.env.get("pathname", None)
        touch_create_folders = bool(self.env.get("touch_create_folders", False))

        file_pathlib = pathlib.Path(pathname)
        if touch_create_folders and not file_pathlib.parent.exists():
            file_pathlib.parent.mkdir(parents=True, exist_ok=True)

        # will create empty file or update timestamp of existing file
        file_pathlib.touch()

        self.env["touch_result"] = "Success"


if __name__ == "__main__":
    PROCESSOR = FileTouch()
    PROCESSOR.execute_shell()
