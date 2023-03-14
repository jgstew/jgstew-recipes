#!/usr/bin/python
"""Extracts the file using shutil unpack_archive.
"""
import shutil

from autopkglib import Processor, ProcessorError

__all__ = ["ExtractorShutilUnpack"]


class ExtractorShutilUnpack(Processor):
    description = "Extracts the archive using 7z."
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to file, defaults to %pathname%",
        },
        "file_format": {
            "required": False,
            "description": "Archive format, if not provided, auto detection used",
        },
        "extract_dir": {
            "required": False,
            "default": "tmp",
            "description": "Output path for the extracted archive.",
        },
        "ignore_errors": {
            "required": False,
            "default": True,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {}

    __doc__ = description

    def main(self):
        """Execution starts here:"""
        file_path = self.env.get("file_path", self.env.get("pathname"))
        file_format = self.env.get("file_format", None)
        working_directory = self.env.get("RECIPE_CACHE_DIR")
        extract_directory = self.env.get("extract_dir", "tmp")
        ignore_errors = self.env.get("ignore_errors", True)
        # verbosity = self.env.get("verbose", 0)

        extract_path = f"{working_directory}/{extract_directory}"

        try:
            if file_format:
                shutil.unpack_archive(file_path, extract_path, file_format)
            else:
                shutil.unpack_archive(file_path, extract_path)

            self.output(f"Extracted Archive Path: {extract_path}")
        except BaseException as err:
            self.output(f"ERROR: {err}", 2)
            if not ignore_errors:
                raise


if __name__ == "__main__":
    processor = ExtractorShutilUnpack()
    processor.execute_shell()
