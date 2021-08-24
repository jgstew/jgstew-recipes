#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryAppend class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TemplateDictionaryAppend"]


class TemplateDictionaryAppend(Processor):  # pylint: disable=invalid-name
    """Takes input dictionary and adds to it"""

    description = __doc__
    input_variables = {
        "dictionary_name": {
            "required": False,
            "default": "template_dictionary",
            "description": "python dictionary to append to",
        },
        "append_key": {
            "required": True,
            "description": "the key to add to the python dictionary",
        },
        "append_value": {
            "required": True,
            "description": "the value to add to the python dictionary",
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

        self.output(f"dictionary_to_append: {dictionary_to_append}", 2)

        append_key = self.env.get("append_key")
        append_value = self.env.get("append_value")

        # ensure it is a dict
        dictionary_to_append = dict(dictionary_to_append)

        dictionary_to_append[append_key] = append_value

        # write back the dict to itself
        self.env[dictionary_name] = dictionary_to_append
        self.env["dictionary_appended"] = dictionary_to_append


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryAppend()
    PROCESSOR.execute_shell()
