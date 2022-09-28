#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileEncodingConvert class"""

import codecs
import shutil

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["FileEncodingConvert"]


class FileEncodingConvert(Processor):  # pylint: disable=invalid-name
    """create file or update its modification time"""

    description = __doc__
    input_variables = {
        "input_file_path": {"required": True, "description": "file to read"},
        "output_file_path": {
            "required": True,
            "description": "file to write to",
        },
        "input_file_encoding": {
            "required": False,
            "default": "utf-16",
            "description": "encoding to read the input file as",
        },
        "output_file_encoding": {
            "required": False,
            "default": "utf-8",
            "description": "encoding to save the output file as",
        },
    }
    output_variables = {
        "file_encoding_result": {"description": ("The result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""
        input_file_path = self.env.get("input_file_path", None)
        output_file_path = self.env.get("output_file_path", None)
        input_file_encoding = str(self.env.get("input_file_encoding", "utf-16"))
        output_file_encoding = str(self.env.get("output_file_encoding", "utf-8"))

        # https://stackoverflow.com/questions/52095133/how-to-convert-a-utf-16-encoded-csv-file-to-utf-8-using-python
        with codecs.open(input_file_path, encoding=input_file_encoding) as input_file:
            with codecs.open(
                output_file_path, "w", encoding=output_file_encoding
            ) as output_file:
                shutil.copyfileobj(input_file, output_file)

        self.env["file_encoding_result"] = "file saved"


if __name__ == "__main__":
    PROCESSOR = FileEncodingConvert()
    PROCESSOR.execute_shell()
