#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileCopyNewest class"""

import pathlib
import shutil

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileCopyNewest"]


class FileCopyNewest(Processor):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "file_path_first": {"required": True, "description": "file path to consider"},
        "file_path_second": {
            "required": True,
            "description": "file path to consider",
        },
    }
    output_variables = {
        "file_copy_newest_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        file_path_first = pathlib.Path(str(self.env.get("file_path_first", None)))
        file_path_second = pathlib.Path(str(self.env.get("file_path_second", None)))

        if not file_path_first.is_file() and not file_path_second.is_file():
            self.env["file_copy_newest_result"] = "ERROR! Neither file found!"
            return None

        if not file_path_first.is_file() and file_path_second.is_file():
            file_copy_newest_result = (
                "first file missing, copying second file to it's location."
            )
            self.env["file_copy_newest_result"] = file_copy_newest_result
            shutil.copy(file_path_second, file_path_first)
            return file_copy_newest_result

        if file_path_first.is_file() and not file_path_second.is_file():
            file_copy_newest_result = (
                "second file missing, copying first file to it's location."
            )
            self.env["file_copy_newest_result"] = file_copy_newest_result
            shutil.copy(file_path_first, file_path_second)
            return file_copy_newest_result

        if file_path_first.is_file() and file_path_second.is_file():
            file_copy_newest_result = "both files present"

            if file_path_first.stat().st_mtime > file_path_second.stat().st_mtime:
                # overwrite file, `copy2` keeps the stats from the original
                shutil.copy2(file_path_first, file_path_second)
                file_copy_newest_result += (
                    ", overwriting the older one with file_path_first"
                )
            else:
                if file_path_first.stat().st_mtime < file_path_second.stat().st_mtime:
                    # overwrite file, `copy2` keeps the stats from the original
                    shutil.copy2(file_path_second, file_path_first)
                    file_copy_newest_result += (
                        ", overwriting the older one with file_path_second"
                    )
                else:
                    file_copy_newest_result += (
                        ", with the same mod time, doing nothing!"
                    )

            self.env["file_copy_newest_result"] = file_copy_newest_result
            return file_copy_newest_result


if __name__ == "__main__":
    PROCESSOR = FileCopyNewest()
    PROCESSOR.execute_shell()
