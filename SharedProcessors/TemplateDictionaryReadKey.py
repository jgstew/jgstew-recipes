#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryReadKey class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TemplateDictionaryReadKey"]


class TemplateDictionaryReadKey(Processor):  # pylint: disable=invalid-name
    """Removes a key from the input dictionary"""

    description = __doc__
    input_variables = {
        "dictionary_name": {
            "required": False,
            "default": "template_dictionary",
            "description": "python dictionary from which to read the key from",
        },
        "dictionary_key": {
            "required": True,
            "description": "the key to read from the python dictionary",
        },
        "dictionary_value_name": {
            "required": False,
            "default": "",
            "description": "the name of the env var to save the value from the dictionary",
        },
    }
    output_variables = {
        "dictionary_value": {"description": ("The value from the dictionary key")},
        "dictionary_value_name": {
            "description": ("name of the variable where the key value is stored")
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        dictionary_name = self.env.get("dictionary_name", "template_dictionary")
        dictionary_to_read = self.env.get(dictionary_name, {})
        dictionary_key = self.env.get("dictionary_key", "version")
        dictionary_value_name = self.env.get("dictionary_value_name", "")

        self.output(f"dictionary key to read: {dictionary_key}", 2)

        # ensure it is a dict
        dictionary_to_read = dict(dictionary_to_read)

        # read the value
        self.env["dictionary_value"] = dictionary_to_read[dictionary_key]

        if dictionary_value_name != "" and dictionary_key:
            # save the value to the custom variable name:
            self.env[dictionary_value_name] = dictionary_to_read[dictionary_key]
            # add the custom var name to the output_variables:
            self.output_variables[dictionary_value_name] = {
                "description": "custom variable name for output",
            }
            # should the `dictionary_value_name` be unset after use?


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryReadKey()
    PROCESSOR.execute_shell()
