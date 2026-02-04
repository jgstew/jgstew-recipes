#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for ContentFromTemplate class"""

import os.path

try:
    import chevron  # pylint: disable=import-error
except ImportError:
    print("ERROR: `chevron` library required.")
    print("https://github.com/jgstew/jgstew-recipes/blob/main/requirements.txt")

try:
    import validate_bes_xml  # pylint: disable=import-error
except ImportError:
    print("ERROR: `validate_bes_xml` module required for bes validation")
    print("Install: pip install --upgrade validate_bes_xml")
    print("See: https://github.com/jgstew/jgstew-recipes/blob/main/requirements.txt")
    validate_bes_xml = None

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

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
            ),
        },
        "template_dictionary": {
            "required": True,
            "description": "python dictionary template with data for template",
        },
        "content_file_pathname": {
            "required": False,
            "default": None,
            "description": "file path to save the XML. Defaults to 'None'",
        },
        "template_partials_path": {
            "required": False,
            "default": ".templates/.partials",
            "description": "folder path to reference Mustache Template Partials",
        },
    }
    output_variables = {
        "content_file_pathname": {
            "description": ("The path of the file saved containing the content_string")
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
        if "template_file_path" in template_dict:
            template_file_path = template_dict["template_file_path"]

        template_file_path = self.env.get("template_file_path", template_file_path)

        self.output(
            "Template File = {template_file_path}".format(
                template_file_path=template_file_path
            ),
            1,
        )

        template_partials_path = self.env.get(
            "template_partials_path", ".templates/.partials"
        )

        if not template_partials_path or not os.path.isdir(template_partials_path):
            self.output(
                f"WARNING: Template Partials Path does not exist (this might be expected if not using them): {template_partials_path}",
                1,
            )
        else:
            self.output(
                f"Template Partials folder found: {template_partials_path}",
                2,
            )

            # if verbosity >= 2, enumerate template partials:
            if int(self.env.get("verbose", 0)) >= 2:
                num_parials = 0
                for root, _, files in os.walk(template_partials_path):
                    for file in files:
                        # if file ends in .mustache
                        if file.endswith(".mustache"):
                            self.output(
                                f"Template Partial found: {os.path.join(root, file)}", 4
                            )
                            num_parials += 1
                self.output(f"Total Template Partials found: {num_parials}", 2)

        self.output(
            f"Full Template Partials path: {os.path.abspath(template_partials_path)}", 3
        )

        # template_file_path still missing, but required
        if not template_file_path:
            raise ProcessorError(
                "`template_file_path` not in template_dict and not passed into function"
            )

        if os.path.isfile(template_file_path) and os.access(
            template_file_path, os.R_OK
        ):
            content_string = chevron.render(
                open(template_file_path), template_dict, template_partials_path
            )
        else:
            raise ProcessorError("ERROR: No Template File Found!")

        self.env["content_string"] = content_string

        return content_string

    def validate_file(self, file_path):
        """validate bes xml file"""
        if validate_bes_xml.validate_bes_xml.validate_xml(file_path):
            self.output("BES File Valid")
        else:
            self.output("ERROR: BES File Invalid!")
            raise ProcessorError(f"ERROR: BES File Invalid! {file_path}")

    def write_file_content(
        self, file_path, content_string
    ):  # pylint: disable=no-self-use
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
        self.output(f"Content String Size = {content_size}", 1)

        if content_file_pathname:
            self.write_file_content(content_file_pathname, content_string)
            self.output(
                "Content File = {content_file_pathname}".format(
                    content_file_pathname=content_file_pathname
                ),
                0,
            )
            if validate_bes_xml:
                if content_file_pathname.endswith(".bes"):
                    self.validate_file(content_file_pathname)

        self.output(
            f"File Content String that was written to `{content_file_pathname}`\n{content_string}",
            4,
        )


if __name__ == "__main__":
    PROCESSOR = ContentFromTemplate()
    PROCESSOR.execute_shell()
