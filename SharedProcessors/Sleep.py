#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for Sleep class"""

import time

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["Sleep"]


class Sleep(Processor):  # pylint: disable=invalid-name
    """Does nothing but delay autopkg for x seconds"""

    description = __doc__
    input_variables = {
        "sleep_seconds": {
            "required": False,
            "default": 15,
            "description": "seconds to sleep",
        },
    }
    output_variables = {}
    __doc__ = description

    def main(self):
        """Execution starts here"""

        sleep_seconds = int(self.env.get("sleep_seconds", 15))

        self.output(f"Pausing Execution for {sleep_seconds} seconds")

        time.sleep(sleep_seconds)

        self.output(f"Resuming Execution after {sleep_seconds} seconds")


if __name__ == "__main__":
    PROCESSOR = Sleep()
    PROCESSOR.execute_shell()
