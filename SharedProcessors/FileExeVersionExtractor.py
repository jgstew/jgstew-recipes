#!/usr/bin/python
"""
Created by James Stewart
Based on ExeVersionExtractor by Rusty Myers
Based on WinInstallerExtractor by Matt Hansen

Extracts version info from .exe file using the 7z utility.
"""

import subprocess

from autopkglib import Processor, ProcessorError, is_windows

__all__ = ["FileExeVersionExtractor"]


class FileExeVersionExtractor(Processor):
    description = "Extracts the Windows archive meta-data using 7z."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
        },
        "ignore_errors": {
            "required": False,
            "default": True,
            "description": "Ignore any errors during the extraction.",
        },
        "sevenzip_path": {
            "required": False,
            "description": """
                Path to 7-Zip binary. 
                Defaults to C:\Program Files\7-Zip\7z.exe on windows
                and Defaults to /usr/local/bin/7z on non-windows.
            """,
        },
        "version_string": {
            "required": False,
            "default": "ProductVersion:",
            "description": "The string to look for in file.",
        },
        "version_first": {
            "required": False,
            "default": False,
            "description": "If True, stop after first match.",
        },
    }
    output_variables = {
        "version": {"description": "Version of exe found."},
    }

    __doc__ = description

    def main(self):
        """Execution starts here"""
        exe_path = self.env.get("exe_path", self.env.get("pathname"))
        version_string = self.env.get("version_string", "ProductVersion:")
        version_first = self.env.get("version_first", False)
        verbosity = self.env.get("verbose", 0)
        ignore_errors = self.env.get("ignore_errors", True)
        extract_flag = "l"

        if is_windows():
            sevenzip_path = self.env.get(
                "sevenzip_path", r"C:\Program Files\7-Zip\7z.exe"
            )
        else:
            sevenzip_path = self.env.get("sevenzip_path", "/usr/local/bin/7z")

        self.output("Extracting: %s" % exe_path)
        cmd = [sevenzip_path, extract_flag, "-y", exe_path]

        self.output(f"Command Line: {cmd}", 2)

        try:
            if verbosity > 1:
                Output = subprocess.check_output(cmd)
            else:
                Output = subprocess.check_output(cmd)
        except BaseException:
            if ignore_errors != "True":
                raise

        self.output(f"Output: \n{Output}\n", 6)

        archiveVersion = ""
        for line in Output.decode().split("\n"):
            if verbosity > 2:
                print(line)
            if version_string in line:
                archiveVersion = line.split()[-1]
                if version_first:
                    break
                continue

        self.env["version"] = archiveVersion.encode("ascii", "ignore")
        self.output("Found Version: %s" % (self.env["version"]))
        # self.output("Extracted Archive Path: %s" % extract_path)


if __name__ == "__main__":
    processor = FileExeVersionExtractor()
    processor.execute_shell()
