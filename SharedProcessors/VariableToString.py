#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2023
#
"""See docstring for VariableToString class"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["VariableToString"]


class VariableToString(Processor):
    """Reads a variable and returns it as a string."""

    description = __doc__

    input_variables = {
        "input_variable": {
            "required": True,
            "description": "The variable to read from.",
        },
        "output_variable": {
            "required": False,
            "description": "Name of the output variable to store the value.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        """Execution starts here"""
        input_variable = self.env.get("input_variable", "")
        output_variable = self.env.get("output_variable", input_variable)

        value = str(self.env.get(input_variable))

        if value is not None:
            self.env[output_variable] = value
            self.output_variables[output_variable] = {
                "description": "the custom output"
            }
        else:
            raise ProcessorError(f"Variable not found.")


if __name__ == "__main__":
    PROCESSOR = VariableToString()
    PROCESSOR.execute_shell()
