#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for DangerousRunProcessors class"""

import autopkglib
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["DangerousRunProcessors"]


class DangerousRunProcessors(Processor):  # pylint: disable=invalid-name
    """a processor that runs other processors"""

    description = __doc__
    input_variables = {
        "dangerous_processor_array": {
            "required": False,
            "default": [],
            "description": "Names of Processors to run.",
        },
    }
    output_variables = {
        "processor_results": {"description": ("The result of the processors")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        # NOTE: can't seem to figure out how to run custom processors, only ones in autopkglib

        # NOTE: because of how this is invoked, it doesn't seem to setup default vars missing from env

        processor_array = self.env.get("dangerous_processor_array", [])

        # RECIPE_PATH = self.env.get("RECIPE_PATH")
        # recipe_inst = autopkglib.recipe_from_file(RECIPE_PATH)
        # if recipe_inst:
        #     self.output(f"valid recipe found at {RECIPE_PATH}")

        for processor_item in processor_array:
            (
                processor_name,
                _,
            ) = autopkglib.extract_processor_name_with_recipe_identifier(processor_item)
            self.output(f"processor_name: {processor_name}")
            processor = autopkglib.get_processor(processor_name)

            processor.main(processor(self.env))


if __name__ == "__main__":
    PROCESSOR = DangerousRunProcessors()
    PROCESSOR.execute_shell()
