#!/usr/local/autopkg/python

import asyncio

from autopkglib import Processor, ProcessorError

# Attempt to import the required library and provide a helpful error if it's not installed.
try:
    from desktop_notifier import DesktopNotifier
except ImportError as e:
    raise ProcessorError(
        "The 'desktop-notifier' library is required for this processor. "
        "Please install it in AutoPkg's Python environment by running: "
        "python -m pip install desktop-notifier"
    ) from e

__all__ = ["Notifier"]


class Notifier(Processor):
    """
    Displays a cross-platform desktop notification using the desktop-notifier library.

    This processor sends a notification to the desktop's notification center.
    Note that the duration of the notification is controlled by the operating
    system's settings and cannot be configured within this processor.
    No callback is associated with the notification.
    """

    description = __doc__
    input_variables = {
        "notification_title": {
            "required": False,
            "description": "The title of the notification.",
            "default": "AutoPkg Run",
        },
        "notification_message": {
            "required": True,
            "description": (
                "The message body of the notification. "
                "Can include AutoPkg variables like %NAME% and %version%."
            ),
        },
        "notification_app_name": {
            "required": False,
            "description": "The name of the application sending the notification.",
            "default": "AutoPkg",
        },
    }
    output_variables = {}

    async def _send_notification_async(self, title, message, app_name):
        """
        Private async method to configure and send the notification.
        This is required because the desktop-notifier library is asynchronous.
        """
        try:
            notifier = DesktopNotifier(app_name=app_name)
            await notifier.send(title=title, message=message)
        except Exception as e:
            # Catch exceptions from the notifier library and raise a ProcessorError
            raise ProcessorError(f"Failed to send notification: {e}") from e

    def main(self):
        """Main entry point for the processor."""
        # Retrieve input variables from the environment, using defaults if not provided
        title = self.env.get(
            "notification_title", self.input_variables["notification_title"]["default"]
        )
        message = self.env.get("notification_message")
        app_name = self.env.get("notification_app_name", self.input_variables["notification_app_name"]["default"])

        # Ensure the required message variable is present
        if not message:
            raise ProcessorError("'notification_message' input variable is required.")

        self.output("Preparing to send notification...")
        self.output(f"  Title: {title}")
        self.output(f"  Message: {message}")
        self.output(f"  App Name: {app_name}")

        # Because the desktop-notifier library is async, we must run its
        # functions within an asyncio event loop.
        try:
            asyncio.run(self._send_notification_async(title, message, app_name))
            self.output("Successfully sent notification to the OS.")
        except Exception as e:
            # Surface any errors that occur during the notification process
            raise ProcessorError(e) from e


if __name__ == "__main__":
    # This allows the processor to be tested directly from the command line
    processor = Notifier()
    processor.execute_shell()
