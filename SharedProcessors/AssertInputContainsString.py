#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for AssertInputContainsString class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["AssertInputContainsString"]


class AssertInputContainsString(Processor):  # pylint: disable=invalid-name
    """checks that assert_string is within input_string"""

    description = __doc__
    input_variables = {
        "input_string": {"required": True, "description": "string to test"},
        "assert_string": {
            "required": True,
            "description": "the string that must be within input_string",
        },
        "raise_error": {
            "required": False,
            "default": True,
            "description": "determines if a failure should raise an error",
        },
    }
    output_variables = {
        "assert_result": {"description": ("The result of the check")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        input_string = self.env.get("input_string")
        assert_string = self.env.get("assert_string")
        raise_error = bool(self.env.get("raise_error", True))

        self.output(f"`{input_string}` must contain `{assert_string}`", 2)

        try:
            assert assert_string in input_string
        except AssertionError:
            self.env["assert_result"] = "ERROR: not found!"
            self.output(f"ERROR: `{assert_string}` not found in `{input_string}`!", 0)
            if raise_error:
                raise

        self.env["assert_result"] = "found!"


if __name__ == "__main__":
    PROCESSOR = AssertInputContainsString()
    PROCESSOR.execute_shell()
