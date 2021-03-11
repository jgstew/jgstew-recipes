#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for BigFixPrefetchItem class"""

import os.path
import site

from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,wrong-import-position,unused-import

# add path this script is in
site.addsitedir(os.path.dirname(os.path.abspath(__file__)))
import prefetch_from_dictionary  # pylint: disable=wrong-import-position


__all__ = ["BigFixPrefetchItem"]


class BigFixPrefetchItem(Processor):  # pylint: disable=invalid-name
    """Takes hash info and returns a bigfix prefetch"""

    description = __doc__
    input_variables = {
        "file_name": {
            "required": False,
            "description": (
                "File name the file should be saved as in the BigFix action. "
                "Defaults to parsed tail of %pathname%."
            ),
        },
        "file_sha1": {
            "required": False,
            "description": "The input file SHA1. Defaults to %filehasher_sha1%"
        },
        "file_sha256": {
            "required": False,
            "description": "The input file SHA256. Defaults to %filehasher_sha256%"
        },
        "file_size": {
            "required": False,
            "description": "The input file size. Defaults to %filehasher_size%"
        },
        "prefetch_type": {
            "required": False,
            "description": "Either 'block' or 'statement'. Defaults to 'statement'"
        }
    }
    output_variables = {
        "bigfix_prefetch_item": {
            "description": "The rendered bigfix prefetch string"
        }
    }
    __doc__ = description

    def get_prefetch(self, prefetch_dictionary):
        """format prefetch from data"""
        bigfix_prefetch_item = prefetch_from_dictionary.prefetch_from_dictionary(
            prefetch_dictionary
        )
        self.env['bigfix_prefetch_item'] = bigfix_prefetch_item
        self.output("Prefetch = {bigfix_prefetch_item}".format(
            bigfix_prefetch_item=bigfix_prefetch_item), 1)

    def main(self):
        """Execution starts here"""
        prefetch_dictionary = {
            'file_name':
                self.env.get(
                    "file_name",
                    os.path.basename(self.env.get("pathname"))
                ),
            'file_size':
                self.env.get(
                    "file_size",
                    self.env.get("filehasher_size")
                ),
            'file_sha1':
                self.env.get(
                    "file_sha1",
                    self.env.get("filehasher_sha1")
                ),
            'file_sha256':
                self.env.get(
                    "file_sha256",
                    self.env.get("filehasher_sha256")
                ),
            'download_url':
                self.env.get(
                    "download_url",
                    self.env.get("url")
                ),
            'prefetch_type':
                self.env.get(
                    "prefetch_type",
                    "statement"
                )
        }
        self.get_prefetch(prefetch_dictionary)


if __name__ == "__main__":
    PROCESSOR = BigFixPrefetchItem()
    PROCESSOR.execute_shell()
