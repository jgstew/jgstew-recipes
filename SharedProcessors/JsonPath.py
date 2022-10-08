#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2022
#
"""See docstring for JsonPath class"""

# pip3 install jsonpath-ng

import json
import os

# https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
import jsonpath_ng.ext
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)


class JsonPath(Processor):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "json_input": {"required": True, "description": "json to get JSONPath from"},
        "json_path": {
            "required": True,
            "description": "JSONPath to read from json",
        },
    }
    output_variables = {
        "json_path_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        json_input = self.env.get("json_input", None)
        json_path = self.env.get("json_path", None)
        json_input_obj = None

        if os.path.isfile(json_input):
            # read json from file:
            with open(json_input, "rb") as json_file:
                json_input_obj = json.load(json_file)
        else:
            # read json from string like:
            json_input_obj = json.loads(json_input)

        jsonpath_expression = jsonpath_ng.ext.parse(json_path)

        json_path_result = jsonpath_expression.find(json_input_obj)[0].value

        self.output(json_path_result, 4)

        self.env["json_path_result"] = json_path_result


if __name__ == "__main__":
    PROCESSOR = JsonPath()
    PROCESSOR.execute_shell()
