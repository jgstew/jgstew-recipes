#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for ContentFromTemplate class"""

import os.path

import chevron  # pylint: disable=import-error

from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,wrong-import-position,unused-import


__all__ = ["ContentFromTemplate"]


class ContentFromTemplate(Processor):  # pylint: disable=invalid-name
    """Takes input dictionary and generates content from a Mustache Template"""

    description = __doc__
    input_variables = {
        "template_file_path": {
            "required": False,
            "description": (
                "The path to the template file to use "
                "Defaults to: template_dictionary['template_file_path']"
            )
        },
        "template_dictionary": {
            "required": True,
            "description": "python dictionary template with data for template"
        },
        "content_file_pathname": {
            "required": False,
            "default": None,
            "description": "file path to save the XML. Defaults to 'None'"
        },
    }
    output_variables = {
        "content_string": {
            "description": (
                "The content output "
                "from mustache template"
            )
        },
        "content_file_pathname": {
            "description": (
                "The path of the file saved "
                "containing the content_string"
            )
        },
    }
    __doc__ = description

    def generate_content(self, template_dict):
        """
        generates content from mustache template

        Keyword arguments:
        template_dict -- dictionary with required keys
        """

        template_file_path = None

        # pylint: disable=line-too-long
        if 'template_file_path' in template_dict:
            template_file_path = template_dict['template_file_path']

        template_file_path = self.env.get("template_file_path", template_file_path)

        self.output("Template File = {template_file_path}".format(
            template_file_path=template_file_path), 1)

        # template_file_path still missing, but required
        if not template_file_path:
            raise ValueError("`template_file_path` not in template_dict and not passed into function")

        if os.path.isfile(template_file_path) and os.access(template_file_path, os.R_OK):
            content_string = chevron.render(open(template_file_path, 'r'), template_dict)
        else:
            raise ProcessorError("ERROR: No Template File Found!")

        self.env['content_string'] = content_string

        return content_string

    def write_file_content(self, file_path, content_string):  # pylint: disable=no-self-use
        """write content to file"""
        file_stream = open(file_path, "w")
        file_stream.write(content_string)
        file_stream.close()

    def main(self):
        """Execution starts here"""

        template_dictionary = self.env.get("template_dictionary")

        content_file_pathname = self.env.get("content_file_pathname", None)

        content_string = self.generate_content(template_dictionary)

        content_size = len(content_string)
        self.output("Content String Size = {content_size}".format(
            content_size=content_size), 1)

        if content_file_pathname:
            self.write_file_content(content_file_pathname, content_string)
            self.output("Content File = {content_file_pathname}".format(
                content_file_pathname=content_file_pathname), 1)


if __name__ == "__main__":
    PROCESSOR = ContentFromTemplate()
    PROCESSOR.execute_shell()
