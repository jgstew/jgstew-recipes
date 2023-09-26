#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2023
#
"""See docstring for DictionaryKeyRead class"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["DictionaryKeyRead"]


class DictionaryKeyRead(Processor):
    """Reads a key-value pair from a Python dictionary."""

    description = __doc__

    input_variables = {
        "input_dictionary": {
            "required": True,
            "description": "The Python dictionary to read from.",
        },
        "dictionary_key": {
            "required": True,
            "description": "The key in the dictionary whose value you want to read.",
        },
        "output_variable": {
            "required": True,
            "description": "Name of the output variable to store the value.",
        },
    }
    output_variables = {}
    __doc__ = description

    def read_dictionary_key(self, input_dictionary, dictionary_key):
        """read the value from the key in the dictionary"""
        try:
            value = input_dictionary.get(dictionary_key)
            return value
        except Exception as e:
            raise ProcessorError(
                f"Failed to read key '{dictionary_key}' from the dictionary: {str(e)}"
            ) from e

    def main(self):
        """Execution starts here"""
        # get name of dictionary to read from:
        input_dictionary_name = self.env.get("input_dictionary", "")
        # get actual dictionary object:
        input_dictionary = self.env.get(input_dictionary_name, None)
        # get name of key:
        dictionary_key = self.env.get("dictionary_key", None)
        # get name of variable to store output:
        output_variable = self.env.get("output_variable", None)

        value = self.read_dictionary_key(input_dictionary, dictionary_key)

        if value is not None:
            self.output(
                f"Read '{dictionary_key}' from dictionary '{input_dictionary_name}': {value}"
            )
            self.env[output_variable] = value
            self.output_variables[output_variable] = {
                "description": "the custom output"
            }
        else:
            raise ProcessorError(f"Key '{dictionary_key}' not found in the dictionary.")


if __name__ == "__main__":
    PROCESSOR = DictionaryKeyRead()
    PROCESSOR.execute_shell()
