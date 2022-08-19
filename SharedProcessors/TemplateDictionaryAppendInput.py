#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryAppendInput class"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TemplateDictionaryAppendInput"]

DEFAULT_input_keys_array = [
    "DisplayName",
    "64BitOnly",
    "32BitOnly",
    "VendorFolder",
    "cmd_args",
    "exe_file",
    "PublicDesktopShortcutFile",
    "cpe_product",
    "cpe_vendor",
    "cpe",
    "content_id_vendor",
    "content_id_product",
]


class TemplateDictionaryAppendInput(Processor):  # pylint: disable=invalid-name
    """Adds Input ENV Vars to Template Dictionary"""

    description = __doc__
    input_variables = {
        "dictionary_name": {
            "required": False,
            "default": "template_dictionary",
            "description": "python dictionary to append to",
        },
        "input_keys_array": {
            "required": False,
            "default": DEFAULT_input_keys_array,
            "description": "the input env keys to append",
        },
        "input_keys_prefix": {
            "required": False,
            "default": "Template_",
            "description": "the prefix of input env keys to append",
        },
    }
    output_variables = {
        "dictionary_name": {"description": ("The appended dictionary name")},
        "dictionary_appended": {"description": ("The appended dictionary")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        dictionary_name = self.env.get("dictionary_name", "template_dictionary")
        dictionary_to_append = self.env.get(dictionary_name, {})
        input_keys_prefix = str(self.env.get("input_keys_prefix", "Template_"))
        input_keys_array = self.env.get("input_keys_array", DEFAULT_input_keys_array)

        if not isinstance(input_keys_array, (list, tuple)):
            self.output(
                f"""
WARNING: input_keys_array was not a list, setting default value:
{DEFAULT_input_keys_array}
                """
            )
            input_keys_array = DEFAULT_input_keys_array

        self.output(f"dictionary_to_append: {dictionary_to_append}", 2)

        # ensure it is a dict
        dictionary_to_append = dict(dictionary_to_append)

        # append matching ENV items to dictionary
        for item in self.env:
            if input_keys_prefix in str(item):
                # print(f"{item} starts with {input_keys_prefix}")
                # get key without prefix:
                append_key = str(item).partition(input_keys_prefix)[2]
                dictionary_to_append[append_key] = self.env[item]
            if item in input_keys_array:
                print(f"{item} in array")
                dictionary_to_append[str(item)] = self.env[item]

        # write back the dict to itself
        self.env[dictionary_name] = dictionary_to_append
        self.env["dictionary_appended"] = dictionary_to_append


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryAppendInput()
    PROCESSOR.execute_shell()
