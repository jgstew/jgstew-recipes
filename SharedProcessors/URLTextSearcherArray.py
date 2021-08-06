#!/usr/local/autopkg/python
"""
See docstring for URLTextSearcherArray class

This processor extends the autopkglib.URLTextSearcher processor
"""

import re

# import sys

# sys.path.append("/Library/AutoPkg")

from autopkglib import ProcessorError  # pylint: disable=import-error,unused-import
from autopkglib.URLTextSearcher import URLTextSearcher  # pylint: disable=import-error

MATCH_MESSAGE = "Found matching text"
NO_MATCH_MESSAGE = "No match found on URL"

__all__ = ["URLTextSearcherArray"]


class URLTextSearcherArray(URLTextSearcher):
    """Downloads a URL using curl and performs a regular expression match
    on the text. Returns an Array of matches instead of first match.
    Requires version 1.4."""

    input_variables = {
        "re_pattern": {
            "description": "Regular expression (Python) to match against page.",
            "required": True,
        },
        "url": {"description": "URL to download", "required": True},
        "result_output_var_name": {
            "description": (
                "The name of the output variable that is returned "
                "by the match. If not specified then a default of "
                '"match" will be used.'
            ),
            "required": False,
            "default": "match",
        },
        "request_headers": {
            "description": (
                "Optional dictionary of headers to include with "
                "the download request."
            ),
            "required": False,
        },
        "curl_opts": {
            "description": (
                "Optional array of curl options to include with "
                "the download request."
            ),
            "required": False,
        },
        "re_flags": {
            "description": (
                "Optional array of strings of Python regular "
                "expression flags. E.g. IGNORECASE."
            ),
            "required": False,
        },
        "full_results": {
            "description": (
                "boolean flag - if true return all results" "Default: False"
            ),
            "required": False,
        },
    }
    output_variables = {
        "result_output_var_name": {
            "description": (
                "First matched sub-pattern from input found on the fetched "
                "URL. Note the actual name of variable depends on the input "
                'variable "result_output_var_name" or is assigned a default of '
                '"match."'
            )
        }
    }

    description = __doc__

    def re_search(self, content):
        """Search for re_pattern in content"""

        re_pattern = re.compile(self.env["re_pattern"], flags=self.prepare_re_flags())
        match_array = re_pattern.findall(content)

        if not match_array:
            raise ProcessorError(f"{NO_MATCH_MESSAGE}: {self.env['url']}")

        # return array of matches
        return match_array

    def main(self):
        """execution starts here"""

        output_var_name = self.env["result_output_var_name"]
        full_results = self.env.get("full_results", None)

        # Prepare curl command
        curl_cmd = self.prepare_curl_cmd()

        # Execute curl command and search in content
        content = self.download_with_curl(curl_cmd)
        match_array = self.re_search(content)

        if not full_results:
            match_array = list(set(match_array))

        self.env[output_var_name] = match_array


if __name__ == "__main__":
    PROCESSOR = URLTextSearcherArray()
    PROCESSOR.execute_shell()
