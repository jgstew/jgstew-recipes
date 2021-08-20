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
        "template_dictionary": {
            "required": True,
            "description": "python dictionary template with data for template",
        },
        "append_dict": {
            "required": True,
            "description": "the dict to add to the template dict",
        },
    }
    output_variables = {
        "template_dictionary": {"description": "The appended dictionary"}
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # get the current dictionary
        template_dictionary = self.env.get("template_dictionary")
        append_dict = self.env.get("append_dict")

        self.output(f"type(template_dictionary): {type(template_dictionary)}", 2)
        self.output(f"type(append_dict): {type(append_dict)}", 2)

        # https://stackoverflow.com/a/8930969/861745
        template_dictionary.update(append_dict)

        # write back the dict to itself
        self.env["template_dictionary"] = template_dictionary


if __name__ == "__main__":
    PROCESSOR = TemplateDictionaryAppendDict()
    PROCESSOR.execute_shell()
