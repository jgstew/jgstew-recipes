#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/_template.py
#
"""See docstring for QRCodeGenerator class"""

import io

# pip install qrcode
import qrcode
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["QRCodeGenerator"]


class QRCodeGenerator(Processor):  # pylint: disable=invalid-name
    """Generates a QR code from a string, printing a scannable version to the log and optionally saving a PNG."""

    description = __doc__
    input_variables = {
        "qr_data": {
            "required": True,
            "description": "The string or URL to encode in the QR code",
        },
        "qr_output_path": {
            "required": False,
            "default": "",
            "description": (
                "Optional path to save the QR code as a PNG. "
                "Empty string (default) skips saving the image."
            ),
        },
        "qr_print_ascii": {
            "required": False,
            "default": True,
            "description": "If True, print a scannable ASCII QR code to the log. Default: True",
        },
    }
    output_variables = {
        "qr_output_path": {
            "description": "The path of the saved PNG, or empty string if not saved",
        },
        "qr_ascii": {
            "description": "The QR code rendered as ASCII text",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        # Reading input_variables
        qr_data = self.env.get("qr_data")
        qr_output_path = self.env.get("qr_output_path", "")
        qr_print_ascii = bool(self.env.get("qr_print_ascii", True))

        # Running Process
        qr_code = qrcode.QRCode(border=2)
        qr_code.add_data(qr_data)
        qr_code.make(fit=True)

        # render scannable ASCII to a string buffer:
        ascii_buffer = io.StringIO()
        qr_code.print_ascii(out=ascii_buffer, invert=True)
        qr_ascii = ascii_buffer.getvalue()

        self.output(f"QR code for: {qr_data}")
        if qr_print_ascii:
            self.output("\n" + qr_ascii)

        if qr_output_path:
            qr_image = qr_code.make_image(fill_color="black", back_color="white")
            qr_image.save(qr_output_path)
            self.output(f"Saved QR code PNG to: {qr_output_path}", 2)

        # Writing output_variables
        self.env["qr_output_path"] = qr_output_path
        self.env["qr_ascii"] = qr_ascii


if __name__ == "__main__":
    PROCESSOR = QRCodeGenerator()
    PROCESSOR.execute_shell()
