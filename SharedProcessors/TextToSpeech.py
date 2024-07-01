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

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["TextToSpeech"]


class TextToSpeech(Processor):  # pylint: disable=invalid-name
    """checks that assert_string is within input_string"""

    description = __doc__
    input_variables = {
        "input_string": {"required": True, "description": "string to say"},
    }
    output_variables = {}
    __doc__ = description

    def speak(self, input_string):
        """speak text aloud"""
        tx = input_string

        # from: https://stackoverflow.com/a/59118441/861745
        syst = platform.system()
        if syst == "Linux" and platform.linux_distribution()[0] == "Ubuntu":
            os.system("spd-say %s" % tx)
        elif syst == "Windows":
            os.system(
                'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(%s);"'
                % tx
            )
        elif syst == "Darwin":
            # add & at end of command to NOT wait.
            os.system("say %s" % tx)
        else:
            # use pyttsx3 to handle other OSes:
            import pyttsx3

            engine = pyttsx3.init()
            engine.say(input_string)
            engine.runAndWait()

        # related: https://stackoverflow.com/a/39647762/861745

    def main(self):
        """Execution starts here"""

        input_string = str(self.env.get("input_string"))

        self.output(f"say `{input_string}` aloud", 1)

        self.speak(input_string)


if __name__ == "__main__":
    PROCESSOR = TextToSpeech()
    PROCESSOR.execute_shell()
