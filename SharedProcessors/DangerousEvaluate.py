#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for DangerousEvaluate class"""


from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

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
            "description": "a string to evaluate as python",
        },
    }
    output_variables = {}
    __doc__ = description

    def main(self):
        """Execution starts here"""

        evaluate_string = self.env.get("evaluate_string")

        self.output(
            "Running Python: \n    {evaluate_string}".format(
                evaluate_string=evaluate_string
            ),
            1,
        )
        try:
            eval(  # pylint: disable=eval-used
                compile(evaluate_string, "<string>", "exec")
            )
        except Exception as err:
            print(err)

        self.output("self.env: \n{self_env}\n".format(self_env=self.env), 5)


if __name__ == "__main__":
    PROCESSOR = DangerousEvaluate()
    PROCESSOR.execute_shell()
