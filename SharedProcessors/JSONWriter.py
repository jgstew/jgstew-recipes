#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/JsonPath.py
#
"""See docstring for JSONWriter class"""

import json

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["JSONWriter"]


class JSONWriter(Processor):  # pylint: disable=invalid-name
    """Writes a value or dictionary from the environment to a JSON file."""

    description = __doc__
    input_variables = {
        "json_input": {
            "required": True,
            "description": (
                "The value to serialize. Accepts a dictionary/list/value directly, "
                "or a JSON-formatted string (which will be parsed then re-serialized)."
            ),
        },
        "json_output_path": {
            "required": True,
            "description": "File path to write the JSON output to",
        },
        "indent": {
            "required": False,
            "default": 4,
            "description": "Number of spaces to indent the JSON output. Default: 4",
        },
        "sort_keys": {
            "required": False,
            "default": False,
            "description": "If True, sort dictionary keys in the output. Default: False",
        },
    }
    output_variables = {
        "json_output_path": {
            "description": "The path of the JSON file that was written",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        json_input = self.env.get("json_input")
        json_output_path = self.env.get("json_output_path")
        indent = int(self.env.get("indent", 4))
        sort_keys = bool(self.env.get("sort_keys", False))

        # If a string was passed, try to parse it so we re-serialize valid JSON.
        # Anything else (dict/list/number/bool) is serialized as-is.
        if isinstance(json_input, str):
            try:
                json_obj = json.loads(json_input)
            except json.JSONDecodeError as err:
                raise ProcessorError(
                    f"json_input is a string but not valid JSON: {err}"
                ) from err
        else:
            json_obj = json_input

        # default=str so non-serializable values don't break the write
        json_text = json.dumps(
            json_obj, indent=indent, sort_keys=sort_keys, default=str
        )

        with open(json_output_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_text)

        self.output(f"Wrote JSON to: {json_output_path}")
        self.output(json_text, 4)

        self.env["json_output_path"] = json_output_path


if __name__ == "__main__":
    PROCESSOR = JSONWriter()
    PROCESSOR.execute_shell()
