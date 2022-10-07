#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2022
#
"""See docstring for FileJsonJq class"""

# on Windows:
#  choco install jq -y
# on MacOS:
#  brew install jq

import os
import subprocess

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# used for self.get_download_dir()
from autopkglib.URLDownloader import URLDownloader

__all__ = ["FileJsonJq"]

JQ_BIN_PATHS = [
    "jq",
    "/usr/bin/jq",
    "/usr/local/bin/jq",
    "/ProgramData/chocolatey/bin/jq",
]


class FileJsonJq(URLDownloader):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "json_input": {"required": True, "description": "json to get jq from"},
        "json_jq": {
            "required": True,
            "description": "jq to read from json file",
        },
        "jq_bin_path": {
            "required": False,
            "default": "jq",
            "description": "Path to the jq binary.",
        },
    }
    output_variables = {
        "json_jq_result": {"description": ("The result")},
        "jq_bin_path": {"description": ("The jq binary used.")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        json_input = self.env.get("json_input", None)
        json_jq = self.env.get("json_jq", None)
        jq_bin_path = self.env.get("jq_bin_path", "jq")

        # if json_input is not file path, make it so.
        if not os.path.isfile(json_input):
            self.output("Writing json_input string to tmp file.")
            download_dir = self.get_download_dir()
            tmp_json_path = download_dir + "/tmp_json_input.json"
            with open(tmp_json_path, "w") as f:
                f.write(json_input)
            json_input = tmp_json_path

        JQ_BIN_PATHS.append(jq_bin_path)
        # search for jq binary executable:
        for path in JQ_BIN_PATHS:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                jq_bin_path = path
                break

        p_jq = subprocess.Popen(
            [jq_bin_path, json_jq, json_input], stdout=subprocess.PIPE
        )
        json_jq_result = p_jq.communicate()[0].decode()

        self.output(json_jq_result, 2)

        self.env["json_jq_result"] = json_jq_result


if __name__ == "__main__":
    PROCESSOR = FileJsonJq()
    PROCESSOR.execute_shell()
