#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryRemove class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TemplateDictionaryRemove"]


class TemplateDictionaryRemove(Processor):  # pylint: disable=invalid-name
    """Removes a key from the input dictionary"""

    description = __doc__
    input_variables = {
        "dictionary_name": {
            "required": False,
            "default": "template_dictionary",
            "description": "python dictionary from which to remove key",
        },
        "remove_key": {
            "required": True,
            "description": "the key to remove from the python dictionary",
        },
    }
    output_variables = {
        "dictionary_name": {"description": ("The reduced dictionary name")},
        "dictionary_reduced": {"description": ("The reduced dictionary")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        dictionary_name = self.env.get("dictionary_name", "template_dictionary")
        dictionary_to_reduce = self.env.get(dictionary_name, {})

        self.output(f"dictionary_to_reduce: {dictionary_to_reduce}", 2)

        remove_key = self.env.get("remove_key")

        # ensure it is a dict
        dictionary_to_reduce = dict(dictionary_to_reduce)

        dictionary_to_reduce.pop(remove_key, None)

        # write back the dict to itself
        self.env[dictionary_name] = dictionary_to_reduce
        self.env["dictionary_reduced"] = dictionary_to_reduce


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryRemove()
    PROCESSOR.execute_shell()
