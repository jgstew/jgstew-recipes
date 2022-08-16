#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
#
"""See docstring for DateTimeFromString class"""

import datetime

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["DateTimeFromString"]


class DateTimeFromString(Processor):  # pylint: disable=invalid-name
    """Takes a datetime string, parses it using `strptime`
     and converts it to a new string using `strftime`

    See Example Test Recipe here:
    - https://github.com/jgstew/jgstew-recipes/blob/main/Test-Recipes/DateTimeFromString.test.recipe.yaml
    """

    description = __doc__
    input_variables = {
        "datetime_string": {
            "required": True,
            "description": "the input string to parse",
        },
        "datetime_strptime": {
            "required": True,
            "description": "the datetime format to parse the input",
        },
        "datetime_strftime": {
            "required": True,
            "description": "the datetime format to parse to the output",
        },
        "datetime_parsed_name": {
            "required": False,
            "default": "datetime_parsed",
            "description": "the env variable to store output as",
        },
    }
    output_variables = {
        "datetime_parsed_name": {
            "description": ("variable datetime parsed result is stored in")
        },
        "datetime_parsed": {"description": ("parsed result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        datetime_parsed_name = self.env.get("datetime_parsed_name", "datetime_parsed")
        datetime_string = self.env.get("datetime_string", "")
        datetime_strptime = self.env.get("datetime_strptime", "")
        datetime_strftime = self.env.get("datetime_strftime", "")

        result = datetime.datetime.strptime(
            datetime_string, datetime_strptime
        ).strftime(datetime_strftime)

        self.env["datetime_parsed_name"] = datetime_parsed_name
        self.env[datetime_parsed_name] = result
        self.env["datetime_parsed"] = result

        # add custom output variable definition:
        if datetime_parsed_name and result:
            self.output_variables[datetime_parsed_name] = {
                "description": "custom datetime output",
            }


if __name__ == "__main__":
    PROCESSOR = DateTimeFromString()
    PROCESSOR.execute_shell()
