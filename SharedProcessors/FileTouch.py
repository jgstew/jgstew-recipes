#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileTouch class"""

import datetime
import os
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
        "touch_time_offset_days": {
            "required": False,
            "default": 0,
            "description": "Create missing folders in path? Default: 0",
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
        touch_time_offset_days = int(self.env.get("touch_time_offset_days", 0))

        file_pathlib = pathlib.Path(pathname)
        if touch_create_folders and not file_pathlib.parent.exists():
            file_pathlib.parent.mkdir(parents=True, exist_ok=True)

        # will create empty file or update timestamp of existing file
        file_pathlib.touch()

        self.env["touch_result"] = "Success"

        if touch_time_offset_days != 0:
            new_mtime = datetime.datetime.today() + datetime.timedelta(
                days=touch_time_offset_days
            )
            os.utime(
                file_pathlib.absolute(), (new_mtime.timestamp(), new_mtime.timestamp())
            )
            self.env["touch_result"] = "file modification time adjusted"


if __name__ == "__main__":
    PROCESSOR = FileTouch()
    PROCESSOR.execute_shell()
