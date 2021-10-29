#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
#
"""See docstring for GetRecipeParentFolderName class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["GetRecipeParentFolderName"]


class GetRecipeParentFolderName(Processor):  # pylint: disable=invalid-name
    """Takes a datetime string and converts it"""

    description = __doc__
    input_variables = {
        "ouput_variable_name": {
            "required": False,
            "default": "VendorFolder",
            "description": "the env var to store the result",
        }
    }
    output_variables = {
        "ouput_variable_name": {"description": ("the env var to store the result")},
        "parent_folder_result": {"description": ("the result")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        ouput_variable_name = self.env.get("ouput_variable_name", "VendorFolder")
        recipe_dir = self.env.get("RECIPE_DIR", "")
        current_variable_value = self.env.get(ouput_variable_name, "")

        # print(f"current_variable_value = `{current_variable_value}`")

        # print(f"ouput_variable_name = {ouput_variable_name}")
        # print(self.env)
        # print(self.env["RECIPE_DIR"])

        parent_folder_name = current_variable_value
        if current_variable_value == "":
            parent_folder_name = os.path.basename(recipe_dir)

        self.env["ouput_variable_name"] = ouput_variable_name
        self.env[ouput_variable_name] = parent_folder_name
        self.env["parent_folder_result"] = parent_folder_name


if __name__ == "__main__":
    PROCESSOR = GetRecipeParentFolderName()
    PROCESSOR.execute_shell()
