#!/usr/local/autopkg/python
#
# Copyright 2025 James Stewart
"""AutoPkg processor to read an environment variable and store its value."""

import os

from autopkglib import Processor, ProcessorError

# The __all__ attribute is used to define what symbols will be exported
# when from <module> import * is used.
__all__ = ["EnvRead"]


class EnvRead(Processor):
    """Reads a value from an environment variable.

    This processor retrieves the value of a specified environment variable
    and stores it into an AutoPkg output variable. The names for both the
    environment variable to be read and the output variable to be created
    are provided as inputs.
    """

    # A description of the processor.
    description = __doc__

    # Define the input variables this processor accepts.
    input_variables = {
        "env_var_name": {
            "required": True,
            "description": "The name of the environment variable to read.",
        },
        "output_var_name": {
            "required": True,
            "description": (
                "The name for the AutoPkg output variable that will store "
                "the environment variable's value."
            ),
        },
    }

    # Define the output variables this processor creates.
    # Since the name of the output variable is dynamic (determined by the
    # 'output_var_name' input), we can't statically declare its name here.
    # We will document this behavior instead.
    output_variables = {
        # The key of the output variable is set dynamically from the
        # `output_var_name` input variable. For example, if `output_var_name`
        # is "my_custom_var", then the output variable will be `self.env["my_custom_var"]`.
    }

    def main(self):
        """Main processing function."""
        # Retrieve the input variables from the AutoPkg environment.
        env_var_to_read = self.env["env_var_name"]
        output_var_to_create = self.env["output_var_name"]

        # Log the action we are about to take.
        self.output(f"Attempting to read environment variable: '{env_var_to_read}'")

        # Use os.getenv() to read the environment variable.
        # This method is safe as it returns None if the variable is not found,
        # rather than raising an exception.
        retrieved_value = os.getenv(env_var_to_read)
        # retrieved_value = self.env.get(env_var_to_read, None)

        # Check if the environment variable was found.
        if retrieved_value is None:
            # If the variable is not set, raise a ProcessorError to stop the recipe run.
            raise ProcessorError(
                f"The environment variable '{env_var_to_read}' is not set."
            )

        # If we successfully retrieved a value, store it in the AutoPkg environment.
        # The key for the new variable is the value of `output_var_to_create`.
        self.env[output_var_to_create] = retrieved_value

        # Log the successful creation of the output variable.
        self.output(f"Stored value in output variable: '{output_var_to_create}'", 2)

        # set output variables so that this is output in verbose output:
        self.output_variables[output_var_to_create] = {
            "description": "the custom output"
        }


if __name__ == "__main__":
    # This block allows the processor to be tested directly from the command line.
    PROCESSOR = EnvRead()
    PROCESSOR.execute_shell()
