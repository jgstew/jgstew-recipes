#!/usr/local/autopkg/python
"""
See docstring for FileGetStat class
"""

import datetime
import os

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileGetStat"]


def timestamp_to_string(timestamp, datetime_format):
    """Convert a Unix timestamp float to a formatted datetime string.

    Args:
        timestamp: Unix timestamp (float) to convert
        datetime_format: strftime format string for the output

    Returns:
        Formatted datetime string, or str(timestamp) if conversion fails
    """
    try:
        datetime_obj = datetime.datetime.fromtimestamp(
            timestamp, tz=datetime.timezone.utc
        )
        return datetime_obj.strftime(datetime_format)
    except BaseException:
        # return bare value if failure:
        return str(timestamp)


class FileGetStat(Processor):  # pylint: disable=too-few-public-methods
    """Gets file statistics including byte size, absolute path, and timestamps (mtime, ctime, atime)."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "file to get info from",
        },
        "file_stat_time_format": {
            "required": False,
            "default": "%Y-%m-%d",
            "description": "format for mtime, ctime, atime",
        },
        "file_stat_time_output_variable": {
            "required": False,
            "default": "SourceReleaseDate",
            "description": "variable to store output in",
        },
        "file_stat_time_output_key": {
            "required": False,
            "default": "oldest_time",
            "description": "the key to get to store in the output",
        },
        # "file_stat_time_output_format": {
        #     "required": False,
        #     "default": "%Y-%m-%d",
        #     "description": "the format of the time for the output variable",
        # },
    }
    output_variables = {
        "file_stat_size": {"description": "the file size"},
        "file_stat_abspath": {"description": "the file absolute path"},
        "file_stat_oldest_time": {"description": "the oldest of the filesystem times"},
        "file_stat_mtime": {"description": "the oldest of the filesystem times"},
        "file_stat_ctime": {"description": "the oldest of the filesystem times"},
        "file_stat_atime": {"description": "the oldest of the filesystem times"},
    }

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        file_stat_time_format = self.env.get("file_stat_time_format", "%Y-%m-%d")
        file_stat_time_output_variable = self.env.get(
            "file_stat_time_output_variable", "SourceReleaseDate"
        )
        file_stat_time_output_key = self.env.get(
            "file_stat_time_output_key", "oldest_time"
        )
        # file_stat_time_output_format = self.env.get(
        #     "file_stat_time_output_format", "%Y-%m-%d"
        # )

        file_stat_result = os.stat(os.path.abspath(file_pathname))

        try:
            oldest_time = file_stat_result.st_mtime
            for file_time in [file_stat_result.st_ctime, file_stat_result.st_atime]:
                if file_time != 0 and file_time < oldest_time:
                    oldest_time = file_time
            self.env["file_stat_oldest_time"] = timestamp_to_string(
                oldest_time, file_stat_time_format
            )
        except BaseException:
            self.env["file_stat_oldest_time"] = ""

        try:
            self.env["file_stat_abspath"] = str(os.path.abspath(file_pathname))
        except BaseException:
            self.env["file_stat_abspath"] = str(file_pathname)

        try:
            self.env["file_stat_size"] = str(file_stat_result.st_size)
        except BaseException:
            self.env["file_stat_size"] = "0"

        try:
            self.env["file_stat_mtime"] = timestamp_to_string(
                file_stat_result.st_mtime, file_stat_time_format
            )
        except BaseException:
            self.env["file_stat_mtime"] = ""

        try:
            self.env["file_stat_ctime"] = timestamp_to_string(
                file_stat_result.st_ctime, file_stat_time_format
            )
        except BaseException:
            self.env["file_stat_ctime"] = ""

        try:
            self.env["file_stat_atime"] = timestamp_to_string(
                file_stat_result.st_atime, file_stat_time_format
            )
        except BaseException:
            self.env["file_stat_atime"] = ""

        try:
            self.env[file_stat_time_output_variable] = self.env[
                f"file_stat_{file_stat_time_output_key}"
            ]
            self.output_variables[file_stat_time_output_variable] = {
                "description": f"custom {file_stat_time_output_key} output"
            }
        except BaseException:
            self.env[file_stat_time_output_variable] = ""


if __name__ == "__main__":
    PROCESSOR = FileGetStat()
    PROCESSOR.execute_shell()
