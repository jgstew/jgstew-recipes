#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/ExtractorSevenZip.py
#
"""See docstring for FileAudioConvert class"""

import os
import subprocess
import sys

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# Add this processor's own directory to sys.path so the shared ffmpeg finder can
# be imported without requiring SharedUtilityMethods to run first in the recipe.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SharedUtilityMethods import find_ffmpeg  # noqa: E402  isort:skip

__all__ = ["FileAudioConvert"]


class FileAudioConvert(Processor):  # pylint: disable=invalid-name
    """Converts an audio file from one format to another (e.g. .oga to .wav) using ffmpeg."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the source audio file, defaults to %pathname%",
        },
        "output_format": {
            "required": False,
            "default": "wav",
            "description": (
                "Target audio format/extension to convert to. Default: 'wav'"
            ),
        },
        "file_path_save": {
            "required": False,
            "default": "",
            "description": (
                "Path to save the converted file. Defaults to the source path "
                "with the output_format extension."
            ),
        },
        "ffmpeg_path": {
            "required": False,
            "default": "",
            "description": "Path to the ffmpeg binary. Defaults to searching common locations.",
        },
        "ffmpeg_args": {
            "required": False,
            "default": [],
            "description": "Array of extra cmd args to pass to ffmpeg (e.g. ['-ar', '44100']).",
        },
        "raise_error": {
            "required": False,
            "default": False,
            "description": (
                "If True, raise an error when ffmpeg is missing. Default: False, so a "
                "host without ffmpeg installed does not break a recipe."
            ),
        },
    }
    output_variables = {
        "file_path_audio": {
            "description": "The path of the converted audio file",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname"))
        output_format = self.env.get("output_format", "wav")
        file_path_save = self.env.get("file_path_save", "")
        ffmpeg_args = self.env.get("ffmpeg_args", [])
        raise_error = bool(self.env.get("raise_error", False))

        if not file_pathname or not os.path.isfile(file_pathname):
            raise ProcessorError(f"Audio file not found: {file_pathname}")

        # default output path: source path with the new extension
        if not file_path_save:
            file_root = os.path.splitext(file_pathname)[0]
            file_path_save = f"{file_root}.{output_format}"

        ffmpeg = find_ffmpeg(self.env.get("ffmpeg_path", ""))
        self.output(f"Using Path to ffmpeg: {ffmpeg}")

        # -y to overwrite, -loglevel error to keep output quiet unless something breaks
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", file_pathname]
        if ffmpeg_args and len(ffmpeg_args) > 0:
            cmd.extend(ffmpeg_args)
        cmd.append(file_path_save)

        self.output(f"ffmpeg cmd line to be executed: {cmd}", 3)

        self.output(f"Converting: {file_pathname} -> {file_path_save}")
        try:
            cmd_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode(
                "utf-8", errors="replace"
            )
            self.output(f"Conversion Process Output: {cmd_output}", 4)
        except subprocess.CalledProcessError as err:
            raise ProcessorError(
                f"Audio conversion failed: {err.output.decode('utf-8', errors='replace')}"
            ) from err
        except FileNotFoundError as err:
            message = f"ffmpeg executable not found ({ffmpeg}). Install ffmpeg to use this processor."
            if raise_error:
                raise ProcessorError(message) from err
            # best-effort: a host without ffmpeg should not break the recipe
            self.output(f"WARNING: {message}", 0)
            self.env["file_path_audio"] = ""
            return

        self.output(f"Converted audio saved to: {file_path_save}")

        self.env["file_path_audio"] = file_path_save


if __name__ == "__main__":
    PROCESSOR = FileAudioConvert()
    PROCESSOR.execute_shell()
