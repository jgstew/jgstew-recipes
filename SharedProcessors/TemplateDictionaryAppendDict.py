#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryAppendDict class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TemplateDictionaryAppendDict"]


class TemplateDictionaryAppendDict(Processor):  # pylint: disable=invalid-name
    """Takes input dictionary and adds to it"""

    description = __doc__
    input_variables = {
        "dictionary_name": {
            "required": False,
            "default": "template_dictionary",
            "description": "python dictionary to append to",
        },
        "append_dict": {
            "required": True,
            "description": "the dict to add to the template dict",
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

        append_dict = self.env.get("append_dict")

        self.output(f"type(dictionary_to_append): {type(dictionary_to_append)}", 2)
        self.output(f"type(append_dict): {type(append_dict)}", 2)

        # https://stackoverflow.com/a/8930969/861745
        dictionary_to_append.update(append_dict)

        # write back the dict to itself
        self.env[dictionary_name] = dictionary_to_append
        self.env["dictionary_appended"] = dictionary_to_append


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryAppendDict()
    PROCESSOR.execute_shell()
