#!/usr/local/autopkg/python
"""
See docstring for FileTextSearcher class
"""

import contextlib
import mmap
import os
import re

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)
from SharedUtilityMethods import SharedUtilityMethods

__all__ = ["FileTextSearcher"]


class FileTextSearcher(SharedUtilityMethods):  # pylint: disable=too-few-public-methods
    """Gets the first executable in the list."""

    description = __doc__
    input_variables = {
        "search_path": {
            "required": True,
            "description": "folder or file to search within",
        },
        "search_pattern": {
            "required": True,
            "description": "the regex pattern to search the file or folders for",
        },
        "search_extension": {
            "required": False,
            "default": "",
            "description": "pattern of files to search within",
        },
        "output_file_path": {
            "required": False,
            "default": "",
            "description": "where to save the output",
        },
        "file_search_results_var": {
            "required": False,
            "default": "",
            "description": "where to save the ouput",
        },
        "unique_results_only": {
            "required": False,
            "default": True,
            "description": "if true, provide only the unique results",
        },
        "sort_results": {
            "required": False,
            "default": True,
            "description": "if true, sort the results",
        },
        "first_result_only": {
            "required": False,
            "default": False,
            "description": "if true, sort the results",
        },
    }
    output_variables = {
        "file_search_results_var": {"description": "the variable name to store output"},
        "output_file_path": {"description": "the file path with the output"},
    }

    def search_in_file(self, file_path, search_pattern):
        """search for regex results in file"""

        re_pattern = re.compile(search_pattern.encode())

        # https://stackoverflow.com/a/54702939/861745
        with open(file_path, "r+") as f:
            # the following allows searching through a large file
            #   without loading it all into memory first
            #   original use case was 300MB+ XML file
            with contextlib.closing(
                mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            ) as data:
                return re.findall(re_pattern, data)

    def main(self):
        """execution starts here"""
        search_path = self.env.get("search_path", None)
        search_pattern = self.env.get("search_pattern", None)
        file_search_results_var = self.env.get("file_search_results_var", "")
        search_extension = self.env.get("search_extension", "")
        output_file_path = self.env.get("output_file_path", "")
        unique_results_only = self.env.get("unique_results_only", True)
        sort_results = self.env.get("sort_results", True)
        first_result_only = self.env.get("first_result_only", False)

        results = []

        if self.verify_file_exists(search_path, False):
            self.output("INFO: file provided instead of folder")
            if search_extension == "" or search_path.endswith(search_extension):
                for item in self.search_in_file(search_path, search_pattern):
                    results.append(item.decode())

        if self.verify_folder_exists(search_path, False):
            self.output("INFO: folder provided")
            for _, _, files in os.walk(search_path):
                for file in files:
                    file_path = os.path.join(search_path, file)
                    if search_extension == "" or file.endswith(search_extension):
                        for item in self.search_in_file(file_path, search_pattern):
                            results.append(item.decode())

        if unique_results_only:
            if sort_results:
                results = list(sorted(set(results)))
            else:
                results = list(set(results))

        self.output(f"number of regex matches: { len(results) }")

        if first_result_only:
            if len(results) > 0:
                results = results[0]
            else:
                results = ""

        if file_search_results_var != "":
            self.env[file_search_results_var] = results
            self.output_variables[file_search_results_var] = {
                "description": "the custom output"
            }

        if output_file_path != "":
            self.output(f" write output to file {output_file_path}")
            # https://stackoverflow.com/a/899149/861745
            with open(output_file_path, "w") as f:
                for item in results:
                    f.write("%s\n" % item)
                # f.write("\n".join(results))


if __name__ == "__main__":
    PROCESSOR = FileTextSearcher()
    PROCESSOR.execute_shell()
