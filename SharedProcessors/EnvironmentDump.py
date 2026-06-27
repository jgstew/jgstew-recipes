#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
"""See docstring for EnvironmentDump class"""

import json

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["EnvironmentDump"]


class EnvironmentDump(Processor):  # pylint: disable=invalid-name
    """Dumps the current AutoPkg environment for debugging, optionally filtered by key substring and/or written to a file."""

    description = __doc__
    input_variables = {
        "key_filter": {
            "required": False,
            "default": "",
            "description": (
                "Case-insensitive substring; only environment keys containing it "
                "are dumped. Empty string (default) dumps all keys."
            ),
        },
        "output_file_path": {
            "required": False,
            "default": "",
            "description": (
                "Optional path to write the dump to as formatted JSON. "
                "Empty string (default) only logs the dump."
            ),
        },
    }
    output_variables = {
        "environment_dump": {
            "description": "The dumped environment as a formatted JSON string",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        key_filter = str(self.env.get("key_filter", "")).lower()
        output_file_path = self.env.get("output_file_path", "")

        if key_filter:
            dumped = {
                key: value
                for key, value in self.env.items()
                if key_filter in key.lower()
            }
        else:
            dumped = dict(self.env)

        # default=str so non-serializable values (e.g. objects) don't break the dump
        environment_dump = json.dumps(dumped, indent=4, sort_keys=True, default=str)

        self.output(f"Environment dump ({len(dumped)} keys):")
        self.output(environment_dump)

        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as dump_file:
                dump_file.write(environment_dump)
            self.output(f"Wrote environment dump to: {output_file_path}", 2)

        self.env["environment_dump"] = environment_dump


if __name__ == "__main__":
    PROCESSOR = EnvironmentDump()
    PROCESSOR.execute_shell()
