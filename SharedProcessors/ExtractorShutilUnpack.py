#!/usr/bin/python
"""Extracts the file using shutil unpack_archive.
"""
import shutil

from autopkglib import Processor, ProcessorError

__all__ = ["ExtractorShutilUnpack"]


class ExtractorShutilUnpack(Processor):
    """This processor unpacks an archive using shutil.unpack_archive"""

    description = "Extracts the archive using 7z."
    input_variables = {
        "file_path": {
            "required": False,
            "description": "Path to file, defaults to %pathname%",
        },
        "file_format": {
            "required": False,
            "description": """The format of the archive
             (e.g. 'zip', 'tar', 'gztar', 'bztar', 'xztar', or '7z').
             If not specified, shutil will attempt to guess based on the file extension.
            """,
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
            err_message = f"ERROR extracting archive '{file_path}': {err}"
            self.output(err_message, 2)
            if not ignore_errors:
                raise ProcessorError(err_message) from err


if __name__ == "__main__":
    processor = ExtractorShutilUnpack()
    processor.execute_shell()
