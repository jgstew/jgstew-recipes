#!/usr/local/autopkg/python
"""
BigFixFileUploader.py
"""

from autopkglib import Processor, ProcessorError
from besapi import besapi
from SharedUtilityMethods import SharedUtilityMethods

__all__ = ["BigFixFileUploader"]


class BigFixFileUploader(SharedUtilityMethods):
    """AutoPkg Processor to upload file to a BigFix root server Uploads

    https://developer.bigfix.com/rest-api/api/upload.html"""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": True,
            "description": "The path to the file to upload",
        },
        "file_sha1": {
            "required": False,
            "default": "",
            "description": "The sha1 hash of the file. Optional.",
        },
        "file_name_override": {
            "required": False,
            "default": "",
            "description": "The filename to use in the prefetch",
        },
    }
    output_variables = {
        "file_upload_prefetch": {"description": "The prefetch for the uploaded file."},
    }
    __doc__ = description

    def main(self):
        """BigFixFileUploader Main Method"""
        file_path = self.env.get("file_path", self.env.get("pathname"))
        file_sha1 = self.env.get("file_sha1", "")
        file_name_override = self.env.get("file_name_override", "")

        self.verify_file_exists(file_path)

        # load besapi conf:
        self.get_config()

        BES_USERNAME = self.env.get("BES_USER_NAME")
        BES_PASSWORD = self.env.get("BES_PASSWORD")
        BES_ROOT_SERVER = self.env.get("BES_ROOT_SERVER")

        # clear password from ENV
        self.env["BES_PASSWORD"] = ""

        # BigFix Server Connection
        # https://github.com/jgstew/besapi/blob/master/src/besapi/besapi.py
        bes_conn = besapi.BESConnection(
            BES_USERNAME, BES_PASSWORD, BES_ROOT_SERVER, verify=False
        )

        # https://developer.bigfix.com/rest-api/api/upload.html
        # https://github.com/jgstew/besapi/blob/ff145f09ee31c4d11d7ad7ea955e51e46b24e168/src/besapi/besapi.py#L508
        upload_result = bes_conn.upload(file_path, file_name_override, file_sha1)

        self.output(upload_result)

        # store result:
        self.env["file_upload_prefetch"] = bes_conn.parse_upload_result_to_prefetch(
            upload_result
        )


if __name__ == "__main__":
    processor = BigFixFileUploader()
    processor.execute_shell()
