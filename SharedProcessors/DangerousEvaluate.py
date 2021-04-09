#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for DangerousEvaluate class"""


from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,wrong-import-position,unused-import


__all__ = ["DangerousEvaluate"]


class DangerousEvaluate(Processor):  # pylint: disable=invalid-name
    """Takes a string and evaluates it as python
        This is a bad idea and dangerous
        This is useful for quick debugging
    """

    description = __doc__
    input_variables = {
        "evaluate_string": {
            "required": True,
            "description": "a string to evaluate as python"
        },
    }
    output_variables = {}
    __doc__ = description


    def main(self):
        """Execution starts here"""

        evaluate_string = self.env.get("evaluate_string")

        self.output("Running: = \n{evaluate_string}".format(
            evaluate_string=evaluate_string), 1)
        # https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile
        eval(compile(evaluate_string, '<string>', 'exec'))  # pylint: disable=eval-used


if __name__ == "__main__":
    PROCESSOR = DangerousEvaluate()
    PROCESSOR.execute_shell()
