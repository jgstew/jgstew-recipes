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
        # "mod_time_offset_days": {
        #     "required": False,
        #     "default": 0,
        #     "description": "number of days in the past to alter the mod time of the file",
        # },
    }
    output_variables = {
        "touch_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        pathname = self.env.get("pathname", None)

        file_pathlib = pathlib.Path(pathname)
        file_pathlib.parent.mkdir(parents=True, exist_ok=True)
        file_pathlib.touch()


if __name__ == "__main__":
    PROCESSOR = FileTouch()
    PROCESSOR.execute_shell()
