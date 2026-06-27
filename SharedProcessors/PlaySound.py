#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/TextToSpeech.py
#
"""See docstring for PlaySound class"""

import os
import platform
import shlex
import shutil

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["PlaySound"]

# Platform-native default sound used when no sound_file_path is provided:
DEFAULT_SOUNDS = {
    "Darwin": "/System/Library/Sounds/Glass.aiff",
    "Linux": "/usr/share/sounds/alsa/Front_Center.wav",
}


class PlaySound(Processor):  # pylint: disable=invalid-name
    """Plays a sound file (or a platform default chime) using platform-native audio tools (afplay, paplay/aplay/ffplay, or PowerShell)."""

    description = __doc__
    input_variables = {
        "sound_file_path": {
            "required": False,
            "default": "",
            "description": (
                "Path to the sound file to play. If empty (default), a "
                "platform-native default sound is used."
            ),
        },
        "raise_error": {
            "required": False,
            "default": False,
            "description": (
                "If True, raise an error when playback fails. Default: False, so a "
                "missing audio device does not break a recipe."
            ),
        },
    }
    output_variables = {
        "sound_file_path": {
            "description": "The resolved path of the sound that was played",
        },
        "sound_command": {
            "description": "The command line used to play the sound",
        },
    }
    __doc__ = description

    def build_command(self, sound_file_path):
        """Build the platform-native command to play a sound file.

        Args:
            sound_file_path: Path to the sound file to play

        Returns:
            The command string to execute, or "" if no player is available
        """
        syst = platform.system()
        quoted = shlex.quote(sound_file_path)

        if syst == "Darwin":
            return f"afplay {quoted}"
        if syst == "Windows":
            return (
                "PowerShell -Command "
                f"\"(New-Object System.Media.SoundPlayer '{sound_file_path}').PlaySync();\""
            )
        if syst == "Linux":
            # prefer PulseAudio, then ALSA, then ffplay (handles more formats):
            if shutil.which("paplay"):
                return f"paplay {quoted}"
            if shutil.which("aplay"):
                return f"aplay {quoted}"
            if shutil.which("ffplay"):
                return f"ffplay -nodisp -autoexit -loglevel quiet {quoted}"
        return ""

    def main(self):
        """Execution starts here."""
        sound_file_path = self.env.get("sound_file_path", "")
        raise_error = bool(self.env.get("raise_error", False))

        # fall back to a platform-native default sound if none was provided:
        if not sound_file_path:
            sound_file_path = DEFAULT_SOUNDS.get(platform.system(), "")

        if not sound_file_path or not os.path.isfile(sound_file_path):
            message = f"Sound file not found: {sound_file_path}"
            if raise_error:
                raise ProcessorError(message)
            self.output(f"WARNING: {message}", 0)
            self.env["sound_file_path"] = sound_file_path
            self.env["sound_command"] = ""
            return

        sound_command = self.build_command(sound_file_path)
        if not sound_command:
            message = f"No audio player found for platform: {platform.system()}"
            if raise_error:
                raise ProcessorError(message)
            self.output(f"WARNING: {message}", 0)
            self.env["sound_file_path"] = sound_file_path
            self.env["sound_command"] = ""
            return

        self.output(f"Playing sound: {sound_file_path}")
        self.output(f"sound cmd: {sound_command}", 3)

        # playback is best-effort: a headless/no-audio host should not break a recipe
        exit_code = os.system(sound_command)
        if exit_code != 0:
            message = f"Sound playback returned non-zero exit code: {exit_code}"
            if raise_error:
                raise ProcessorError(message)
            self.output(f"WARNING: {message}", 1)

        self.env["sound_file_path"] = sound_file_path
        self.env["sound_command"] = sound_command


if __name__ == "__main__":
    PROCESSOR = PlaySound()
    PROCESSOR.execute_shell()
