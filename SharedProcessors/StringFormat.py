#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/TextSubstitutionRegEx.py
#
"""See docstring for StringFormat class"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["StringFormat"]


class StringFormat(Processor):  # pylint: disable=invalid-name
    """Formats a string using Python str.format(), supporting zero-padding, alignment, and named substitutions."""

    description = __doc__
    input_variables = {
        "format_string": {
            "required": True,
            "description": (
                "A Python format string. The single value is available as `{}`, "
                "`{0}`, or `{value}`; named values from format_kwargs are available "
                "by their key, e.g. '{name}-v{version}' or '{value:0>5}'."
            ),
        },
        "format_value": {
            "required": False,
            "default": "",
            "description": (
                "A single value to format, referenced as `{}`, `{0}`, or `{value}`. "
                "Default: empty string."
            ),
        },
        "format_kwargs": {
            "required": False,
            "default": {},
            "description": (
                "A dictionary of named values referenced by key in the format string. "
                "Keys here override the built-in `value` key. Default: empty dict."
            ),
        },
    }
    output_variables = {
        "formatted_string": {
            "description": "The result of applying the format string",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        format_string = self.env.get("format_string")
        format_value = self.env.get("format_value", "")
        format_kwargs = self.env.get("format_kwargs", {})

        # Running Process
        # `value` is the built-in alias for the single positional value;
        # any matching key in format_kwargs takes precedence.
        kwargs = {"value": format_value}
        kwargs.update(format_kwargs)

        try:
            formatted_string = format_string.format(format_value, **kwargs)
        except (KeyError, IndexError, ValueError) as err:
            raise ProcessorError(
                f"Failed to format string `{format_string}`: {err}"
            ) from err

        self.output(f"Formatted string: {formatted_string}")

        # Writing output_variables
        self.env["formatted_string"] = formatted_string


if __name__ == "__main__":
    PROCESSOR = StringFormat()
    PROCESSOR.execute_shell()
