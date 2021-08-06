#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TemplateDictionaryAppend class"""


from autopkglib import (
    Processor,
    ProcessorError,
)  # pylint: disable=import-error,wrong-import-position,unused-import


__all__ = ["TemplateDictionaryAppend"]


class TemplateDictionaryAppend(Processor):  # pylint: disable=invalid-name
    """Takes input dictionary and adds to it"""

    description = __doc__
    input_variables = {
        "template_dictionary": {
            "required": True,
            "description": "python dictionary template with data for template",
        },
        "append_key": {
            "required": True,
            "description": "the key to add to the python dictionary template",
        },
        "append_value": {
            "required": True,
            "description": "the value to add to the python dictionary template",
        },
    }
    output_variables = {
        "template_dictionary": {"description": ("The appended dictionary")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        template_dictionary = self.env.get("template_dictionary")
        append_key = self.env.get("append_key")
        append_value = self.env.get("append_value")

        template_dictionary[append_key] = append_value

        # write back the dict to itself
        self.env["template_dictionary"] = template_dictionary


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryAppend()
    PROCESSOR.execute_shell()
