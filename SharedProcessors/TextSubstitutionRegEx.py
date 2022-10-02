#!/usr/local/autopkg/python
#
# Copyright 2022 James Stewart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for TextSubstitutionRegEx class"""

import re

from autopkglib import Processor, ProcessorError

__all__ = ["TextSubstitutionRegEx"]


class TextSubstitutionRegEx(Processor):
    """Parses a string using regular expression and substitute."""

    input_variables = {
        "re_pattern": {
            "description": "Regular expression (Python) to match against text to substitute.",
            "required": True,
        },
        "re_substitution": {
            "description": "Text to substitue from the Regular Expression Match.",
            "required": True,
        },
        "input_string": {"description": "String to search", "required": True},
        "result_output_var_name": {
            "description": (
                "The name of the output variable that is returned "
                "by the match. If not specified then a default of "
                '"result_substitution" will be used.'
            ),
            "required": False,
            "default": "result_substitution",
        },
    }
    output_variables = {
        "result_output_var_name": {
            "description": (
                "First matched sub-pattern from input found on the string. "
                "Note the actual name of variable depends on the input "
                'variable "result_output_var_name" or is assigned a default of '
                '"result_substitution."'
            )
        }
    }

    description = __doc__

    def main(self):
        re_pattern = self.env.get("re_pattern", None)
        re_substitution = self.env.get("re_substitution", None)
        input_string = self.env.get("input_string", None)
        result_output_var_name = self.env.get(
            "result_output_var_name", "result_substitution"
        )

        # re.sub(pattern, replace, string) is the equivalent of s/pattern/replace/ in SED
        result_substitution = re.sub(re_pattern, re_substitution, input_string)

        self.env[result_output_var_name] = result_substitution

        self.output_variables[result_output_var_name] = {
            "description": "the custom output variable"
        }


if __name__ == "__main__":
    PROCESSOR = TextSubstitutionRegEx
    PROCESSOR.execute_shell()
