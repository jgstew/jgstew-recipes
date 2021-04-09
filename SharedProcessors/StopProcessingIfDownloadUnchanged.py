#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for StopProcessingIfDownloadUnchanged class"""

from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,unused-import

__all__ = ["StopProcessingIfDownloadUnchanged"]


class StopProcessingIfDownloadUnchanged(Processor):  # pylint: disable=invalid-name
    """Stops processing if download unchanged in pure python"""

    description = __doc__
    input_variables = {
        "env_var_name": {
            "description": (
                "Environment Variable to test it's contents"
            ),
            "required": False,
            "default": "download_changed",
        },
        "env_var_value_test": {
            "description": (
                "Value to test if it is in the Variable"
            ),
            "required": False,
            "default": "FalsE",
        },
        "env_var_value_case_insensitive": {
            "description": (
                "boolean for case insensitive comparison"
            ),
            "required": False,
            "default": True,
        }
    }
    output_variables = {
        "stop_processing_recipe": {
            "description": "Boolean. Should we stop processing the recipe?"
        }
    }
    __doc__ = description


    def main(self):
        """Execution starts here"""
        env_var_value_case_insensitive = self.env.get("env_var_value_case_insensitive")
        #print(env_var_value_case_insensitive)
        env_var_value_test = self.env.get("env_var_value_test")
        #print(env_var_value_test)
        env_var_value_real = self.env.get(self.env.get("env_var_name"))
        #print(env_var_value_real)
        if env_var_value_case_insensitive:
            env_var_value_test = str(env_var_value_test).upper()
            env_var_value_real = str(env_var_value_real).upper()

        if str(env_var_value_test) in str(env_var_value_real):
            self.env["stop_processing_recipe"] = True
        else:
            self.env["stop_processing_recipe"] = False


if __name__ == "__main__":
    PROCESSOR = StopProcessingIfDownloadUnchanged()
    PROCESSOR.execute_shell()
