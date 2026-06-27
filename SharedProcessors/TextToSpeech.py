#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2024
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for TextToSpeech class"""

import os
import platform
import shutil
import subprocess

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TextToSpeech"]

# Hard cap on how long a single speech attempt may run, so a stuck TTS backend
# (e.g. spd-say waiting on an absent speech-dispatcher daemon) can never hang
# the recipe indefinitely.
TTS_TIMEOUT_SECONDS = 60


class TextToSpeech(Processor):  # pylint: disable=invalid-name
    """Converts a text string to audible speech using platform-native TTS tools (say, spd-say, PowerShell, or pyttsx3)."""

    description = __doc__
    input_variables = {
        "input_string": {"required": True, "description": "string to say"},
    }
    output_variables = {}
    __doc__ = description

    @staticmethod
    def _speech_available():
        """Return False on a headless host where TTS would hang or fail.

        On Linux native TTS (spd-say) needs a running speech-dispatcher daemon and
        an audio device; in headless CI neither is present and the call can block
        indefinitely. macOS and Windows are assumed to have TTS available.

        Returns:
            True if text-to-speech can plausibly be produced.
        """
        if platform.system() == "Linux":
            return bool(
                os.environ.get("DBUS_SESSION_BUS_ADDRESS") or os.environ.get("DISPLAY")
            )
        return True

    def speak(self, input_string):
        """Convert text to speech using platform-native TTS tools.

        Uses say on macOS, spd-say on Linux, PowerShell SpeechSynthesizer on Windows,
        or pyttsx3 as a cross-platform fallback. Each backend is run with a timeout
        so a stuck TTS service cannot hang the recipe.

        Args:
            input_string: Text string to speak aloud
        """
        # from: https://stackoverflow.com/a/59118441/861745
        syst = platform.system()
        try:
            # change check to look for command existence, rather than Ubuntu specific:
            if syst == "Linux" and shutil.which("spd-say") is not None:
                subprocess.run(
                    ["spd-say", input_string], timeout=TTS_TIMEOUT_SECONDS, check=False
                )
            elif syst == "Windows":
                # escape single quotes for the PowerShell single-quoted string:
                ps_text = input_string.replace("'", "''")
                subprocess.run(
                    [
                        "PowerShell",
                        "-Command",
                        "Add-Type -AssemblyName System.Speech; "
                        "(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
                        f".Speak('{ps_text}');",
                    ],
                    timeout=TTS_TIMEOUT_SECONDS,
                    check=False,
                )
            elif syst == "Darwin":
                subprocess.run(
                    ["say", input_string], timeout=TTS_TIMEOUT_SECONDS, check=False
                )
            else:
                # use pyttsx3 to handle other OSes:
                import pyttsx3

                engine = pyttsx3.init()
                engine.say(input_string)
                engine.runAndWait()
        except subprocess.TimeoutExpired:
            self.output("WARNING: text-to-speech timed out; skipping.", 0)
        except Exception as err:  # pylint: disable=broad-except
            self.output(f"WARNING: text-to-speech failed: {err}", 0)

        # related: https://stackoverflow.com/a/39647762/861745

    def main(self):
        """Execution starts here."""
        input_string = str(self.env.get("input_string"))

        self.output(f"say `{input_string}` aloud", 1)

        # skip cleanly on a headless host (no audio/desktop to speak to):
        if not self._speech_available():
            self.output(
                "No desktop session detected (headless); skipping text-to-speech.", 1
            )
            return

        self.speak(input_string)


if __name__ == "__main__":
    PROCESSOR = TextToSpeech()
    PROCESSOR.execute_shell()
