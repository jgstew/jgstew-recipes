#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# based upon: https://groups.google.com/g/autopkg-discuss/c/CXoGpW1T404
#
"""See docstring for DangerousCommandRunner class"""

import os
import subprocess

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["DangerousCommandRunner"]


class DangerousCommandRunner(Processor):  # pylint: disable=invalid-name
    """Runs a command using subprocess

    You should probably not use this processor, as it is dangerous.
    It is intended to be used for testing and debugging purposes only.
    It is not recommended to use this processor in production recipes."""

    input_variables = {
        "command_path": {
            "required": True,
            "description": "External command.",
        },
        "command_args": {
            "required": False,
            "description": ("Optional array of arguments for external command."),
        },
    }
    output_variables = {
        "command_output": {
            "description": "Output of script.",
        },
        "command_return_code": {
            "description": "Success status of script.",
        },
    }

    description = __doc__

    def main(self):
        """Run external script at path defined in command_path
        with arguments provided in command_args."""

        command = [self.env["command_path"]]
        command.extend(self.env["command_args"])
        args_oneline = " ".join(map(str, self.env["command_args"]))

        try:
            proc = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            (out, err_out) = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                "Script '%s' execution failed with error code %d: %s"
                % (self.env["command_path"], err.errno, err.strerror)
            ) from err
        if proc.returncode:
            self.env["command_return_code"] = proc.returncode
        if proc.returncode != 0:
            self.output("Output: %s" % out)
            raise ProcessorError(
                "Script '%s' failed with err_out: '%s'\nOutput: %s"
                % (self.env["command_path"], err_out, out)
            )

        self.output(
            "Script '%s' was run successfully!\nArguments sent:\n'%s'\nOutput: %s"
            % (self.env["command_path"], args_oneline, out),
            4,
        )

        if out:
            self.env["command_output"] = out.decode()


if __name__ == "__main__":
    PROCESSOR = DangerousCommandRunner()
    PROCESSOR.execute_shell()
