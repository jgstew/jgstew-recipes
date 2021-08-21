#!/usr/bin/python
"""
Created by James Stewart

Does nothing on it's own

Contains Shared Class Method Utility Functions
"""

import errno
import os

from autopkglib import Processor, ProcessorError

__all__ = ["SharedUtilityMethods"]


class SharedUtilityMethods(Processor):
    """Provides shared class methods."""

    input_variables = {}
    output_variables = {}

    def verify_file_exists(self, file_path, raise_error=True):
        """verify file exists, raise error if not"""
        if not os.path.isfile(file_path):
            self.output(f"ERROR: file missing! {file_path}", 0)
            if raise_error:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), file_path
                )
        return file_path

    def main(self):
        """Execution starts here"""
        self.output("ERROR: main() Does Nothing! Must Override!", 0)


if __name__ == "__main__":
    print("SharedUtilityMethods: Does Nothing! Must Override!")
