#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Link:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/_template.py
#
"""See docstring for HelloWorld class

to run this directly from bash, use:

```
PYTHONPATH="../autopkg/Code:SharedProcessors" ./.venv/bin/python <<EOF
from _template import HelloWorld
p = HelloWorld({})
p.main()
print(p.env)
EOF
```

"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["HelloWorld"]


class HelloWorld(Processor):  # pylint: disable=invalid-name
    """Greets a named recipient and returns the greeting as a string."""

    description = __doc__
    input_variables = {
        "greeting_name": {
            "required": False,
            "default": "World",
            "description": "Name to include in the greeting (default: World)",
        },
    }
    output_variables = {
        "greeting_result": {
            "description": "The full greeting string that was produced",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        greeting_name = str(self.env.get("greeting_name", "World"))

        greeting = f"Hello, {greeting_name}!"

        self.output(greeting)

        self.env["greeting_result"] = greeting


if __name__ == "__main__":
    PROCESSOR = HelloWorld()
    PROCESSOR.execute_shell()
