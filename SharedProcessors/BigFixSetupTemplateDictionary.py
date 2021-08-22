#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for BigFixSetupTemplateDictionary class"""

import os.path

# site.addsitedir("/Library/AutoPkg")
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# add path this script is in
# site.addsitedir(os.path.dirname(os.path.abspath(__file__)))
from generate_bes_from_template import (  # pylint: disable=wrong-import-position
    generate_bes_from_template,
)

# import site


__all__ = ["BigFixSetupTemplateDictionary"]


class BigFixSetupTemplateDictionary(Processor):  # pylint: disable=invalid-name
    """Takes input and generates bigfix content from a Mustache Template"""

    description = __doc__
    input_variables = {
        "file_name": {
            "required": False,
            "description": (
                "File name the file should be saved as in the BigFix action. "
                "Defaults to %file_path% "
                "otherwise from parsed tail of %pathname%."
            ),
        },
        "template_prefetch": {
            "required": False,
            "description": "The input file SHA1. Defaults to %bigfix_prefetch_item%",
        },
        "template_file_size": {
            "required": False,
            "description": "The input file size. Defaults to %filehasher_size%",
        },
        "prefetch_type": {
            "required": False,
            "default": "statement",
            "description": "Either 'block' or 'statement'. Defaults to 'statement'",
        },
        "template_version": {
            "required": False,
            "description": "version to use. Defaults to 'version'",
        },
    }
    output_variables = {
        "template_dictionary": {
            "description": "python dictionary template with data for template"
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        # get download_info dictionary or empty dictionary
        download_info = self.env.get("download_info", {})

        # get for default use
        pathname_base = None
        pathname = self.env.get("pathname", None)
        if pathname:
            pathname_base = os.path.basename(pathname)

        # if no file_size then set to 0
        if "file_size" not in download_info:
            download_info["file_size"] = 0

        template_dict = {
            "file_name": self.env.get("file_name", pathname_base),
            "prefetch": self.env.get(
                "template_prefetch", self.env.get("bigfix_prefetch_item")
            ),
            "version": self.env.get("template_version", self.env.get("version", "")),
            "DownloadSize": self.env.get(
                "template_file_size",
                self.env.get("filehasher_size", download_info["file_size"]),
            ),
            "prefetch_type": self.env.get("prefetch_type", "statement"),
            #'template_file_path': "./BigFix/FixletDebugger-Win.bes.mustache"
        }
        self.env[
            "template_dictionary"
        ] = generate_bes_from_template.get_missing_bes_values(template_dict)


if __name__ == "__main__":
    PROCESSOR = BigFixSetupTemplateDictionary()
    PROCESSOR.execute_shell()
