#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileXmlXpath class"""

import os
import pathlib

import lxml
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileXmlXpath"]


class FileXmlXpath(Processor):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "pathname": {"required": True, "description": "xml file to get xpath from"},
        "xml_xpath": {
            "required": True,
            "description": "xpath to read from xml file",
        },
        "xml_only_first": {
            "required": False,
            "default": False,
            "description": "return only the first result",
        },
        "xml_only_last": {
            "required": False,
            "default": False,
            "description": "return only the last result",
        },
    }
    output_variables = {
        "xml_xpath_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        pathname = self.env.get("pathname", None)
        xml_xpath = self.env.get("xml_xpath", None)
        xml_only_first = self.env.get("xml_only_first", False)
        xml_only_last = self.env.get("xml_only_last", False)

        xml_root = lxml.etree.parse(pathname)
        xml_xpath_result = xml_root.xpath(xml_xpath)

        self.output(xml_xpath_result, 2)

        if xml_only_first:
            self.env["xml_xpath_result"] = xml_xpath_result[0]
        elif xml_only_last:
            self.env["xml_xpath_result"] = xml_xpath_result[-1]
        else:
            self.env["xml_xpath_result"] = xml_xpath_result


if __name__ == "__main__":
    PROCESSOR = FileXmlXpath()
    PROCESSOR.execute_shell()
