#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileGetStat.py
#
"""See docstring for FileGetMetadata class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

# pip install hachoir
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

__all__ = ["FileGetMetadata"]


class FileGetMetadata(Processor):  # pylint: disable=invalid-name
    """Extracts metadata (duration, dimensions, sample rate, codec, etc.) from many file types (audio, video, images, archives) using hachoir."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the file to extract metadata from, defaults to %pathname%",
        },
    }
    output_variables = {
        "file_metadata": {
            "description": "Dictionary of all extracted metadata key/value pairs",
        },
        "file_metadata_mime": {
            "description": "The detected MIME type, or empty string if unknown",
        },
        "file_metadata_duration_seconds": {
            "description": "Media duration in seconds (audio/video), or empty string",
        },
        "file_metadata_width": {
            "description": "Image/video width in pixels, or empty string",
        },
        "file_metadata_height": {
            "description": "Image/video height in pixels, or empty string",
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))

        if not file_pathname or not os.path.isfile(file_pathname):
            raise ProcessorError(f"File not found: {file_pathname}")

        parser = createParser(file_pathname)
        if not parser:
            raise ProcessorError(f"Unable to parse file for metadata: {file_pathname}")

        with parser:
            metadata = extractMetadata(parser)

        if not metadata:
            raise ProcessorError(
                f"No metadata could be extracted from: {file_pathname}"
            )

        # build a flat dict of all metadata using hachoir's machine-readable keys:
        metadata_dict = {}
        for item in metadata:
            if item.values:
                metadata_dict[item.key] = str(item.values[0].value)

        # reset promoted outputs to empty defaults:
        self.env["file_metadata_mime"] = ""
        self.env["file_metadata_duration_seconds"] = ""
        self.env["file_metadata_width"] = ""
        self.env["file_metadata_height"] = ""

        if metadata.has("mime_type"):
            self.env["file_metadata_mime"] = str(metadata.get("mime_type"))
        if metadata.has("duration"):
            # duration is a datetime.timedelta; expose total seconds for easy use
            try:
                self.env["file_metadata_duration_seconds"] = str(
                    metadata.get("duration").total_seconds()
                )
            except AttributeError:
                self.env["file_metadata_duration_seconds"] = str(
                    metadata.get("duration")
                )
        if metadata.has("width"):
            self.env["file_metadata_width"] = str(metadata.get("width"))
        if metadata.has("height"):
            self.env["file_metadata_height"] = str(metadata.get("height"))

        self.output(
            f"Extracted {len(metadata_dict)} metadata fields from {file_pathname}"
        )
        self.output(metadata_dict, 2)

        self.env["file_metadata"] = metadata_dict


if __name__ == "__main__":
    PROCESSOR = FileGetMetadata()
    PROCESSOR.execute_shell()
