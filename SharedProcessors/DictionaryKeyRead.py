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
        try:
            value = input_dictionary.get(dictionary_key)
            return value
        except Exception as e:
            raise ProcessorError(
                f"Failed to read key '{dictionary_key}' from the dictionary: {str(e)}"
            )

    def main(self):
        input_dictionary = self.env.get("input_dictionary")
        input_dictionary = self.env.get(input_dictionary)
        dictionary_key = self.env.get("dictionary_key")
        output_variable = self.env.get("output_variable")

        value = self.read_dictionary_key(input_dictionary, dictionary_key)

        if value is not None:
            self.output(f"Read '{dictionary_key}' from the dictionary: {value}")
            self.env[output_variable] = value
        else:
            raise ProcessorError(f"Key '{dictionary_key}' not found in the dictionary.")


if __name__ == "__main__":
    PROCESSOR = DictionaryKeyRead()
    PROCESSOR.execute_shell()
