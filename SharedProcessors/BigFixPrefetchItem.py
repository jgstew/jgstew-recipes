#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for BigFixPrefetchItem class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# add path this script is in
# site.addsitedir(os.path.dirname(os.path.abspath(__file__)))
from bigfix_prefetch import (  # pylint: disable=wrong-import-position
    prefetch_from_dictionary,
)

# import site


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
            "description": "The input file SHA1. Defaults to %filehasher_sha1%",
        },
        "file_sha256": {
            "required": False,
            "description": "The input file SHA256. Defaults to %filehasher_sha256%",
        },
        "file_size": {
            "required": False,
            "description": "The input file size. Defaults to %filehasher_size%",
        },
        "prefetch_type": {
            "required": False,
            "description": "Either 'block' or 'statement'. Defaults to 'statement'",
        },
        "prefetch_url": {
            "required": False,
            "description": "Url to use in Prefetch or the dictionary key to use"
            " defaults to url or download_url",
        },
    }
    output_variables = {
        "bigfix_prefetch_item": {
            "description": (
                "The bigfix prefetch string output " "from prefetch_from_dictionary"
            )
        }
    }
    __doc__ = description

    def get_prefetch(self, prefetch_dictionary):
        """
        formats prefetch from data in dictionary

        Keyword arguments:
        prefetch_dictionary -- dictionary with required keys
        """
        bigfix_prefetch_item = prefetch_from_dictionary.prefetch_from_dictionary(
            prefetch_dictionary
        )
        self.env["bigfix_prefetch_item"] = bigfix_prefetch_item
        self.output(
            "Prefetch = {bigfix_prefetch_item}".format(
                bigfix_prefetch_item=bigfix_prefetch_item
            ),
            1,
        )

    def main(self):
        """Execution starts here"""
        # use download_info dictionary from URLDownloaderPython if available
        prefetch_dictionary = self.env.get("download_info", None)
        prefetch_url = self.env.get("prefetch_url", None)

        if prefetch_dictionary:
            if prefetch_url:
                # if `url` then use that key
                if prefetch_url == "url":
                    prefetch_dictionary["download_url"] = prefetch_dictionary["url"]
                else:
                    # if `download_url` do nothing, default
                    if prefetch_url != "download_url":
                        # otherwise assume real URL provided and use that
                        prefetch_dictionary["download_url"] = prefetch_url
            else:
                # default behavior if `prefetch_url` unspecified:
                prefetch_dictionary["download_url"] = prefetch_dictionary["url"]
        else:
            # if no download_info dictionary, then create it:
            prefetch_dictionary = {
                "file_name": self.env.get(
                    "file_name", os.path.basename(self.env.get("pathname"))
                ),
                "file_size": self.env.get("file_size", self.env.get("filehasher_size")),
                "file_sha1": self.env.get("file_sha1", self.env.get("filehasher_sha1")),
                "file_sha256": self.env.get(
                    "file_sha256", self.env.get("filehasher_sha256")
                ),
                "download_url": self.env.get(
                    "prefetch_url", self.env.get("url", self.env.get("download_url"))
                ),
            }
        prefetch_dictionary["prefetch_type"] = self.env.get(
            "prefetch_type", "statement"
        )
        self.get_prefetch(prefetch_dictionary)

        self.output("self.env: \n{self_env}\n".format(self_env=self.env), 4)


if __name__ == "__main__":
    PROCESSOR = BigFixPrefetchItem()
    PROCESSOR.execute_shell()
