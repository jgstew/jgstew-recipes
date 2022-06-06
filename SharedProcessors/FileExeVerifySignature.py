#!/usr/local/autopkg/python
"""
See docstring for FileExeVerifySignature class
"""

from autopkglib import (  # pylint: disable=import-error,unused-import
    Processor,
    ProcessorError,
)
from signify.authenticode.signed_pe import SignedPEFile
from signify.exceptions import SignedPEParseError

__all__ = ["FileExeVerifySignature"]


class FileExeVerifySignature(Processor):  # pylint: disable=too-few-public-methods
    """
    validates windows binary signature and gets the signature date if available

    See example:
    - https://github.com/jgstew/tools/blob/master/Python/get_pefile_signify.py
    - https://stackoverflow.com/a/72520692/861745
    """

    description = __doc__
    input_variables = {
        "file_pathname": {"required": False, "description": "file path to verify"},
    }
    output_variables = {
        "file_signature_date": {"description": "the base64 encoded string"},
        "file_signature_result": {"description": "the base64 encoded string"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        self.env["file_signature_date"] = ""
        self.env["file_signature_result"] = "UnknownError"
        if file_pathname:
            with open(file_pathname, "rb") as file_io:
                pefile = SignedPEFile(file_io)
                try:
                    # https://github.com/jgstew/tools/blob/master/Python/get_pefile_signify_time.py
                    self.env["file_signature_date"] = str(
                        list(pefile.signed_datas)[0]
                        .signer_infos[0]
                        .countersigner.signing_time
                    )
                except Exception:
                    # print(err)
                    pass
                try:
                    sig_result, sig_explain = pefile.explain_verify()
                    # print(sig_result)
                    # print(sig_explain)
                    if str(sig_result) == "AuthenticodeVerificationResult.OK":
                        self.env["file_signature_result"] = "VALID"
                    elif str(sig_result) == "AuthenticodeVerificationResult.NOT_SIGNED":
                        self.env["file_signature_result"] = "NOT_SIGNED"
                    else:
                        self.env["file_signature_result"] = (
                            str(sig_result) + ":" + str(sig_explain)
                        )
                except Exception as err:
                    print(err)
                    self.env["file_signature_result"] = "ERROR_NOT_VALID"


if __name__ == "__main__":
    PROCESSOR = FileExeVerifySignature()
    PROCESSOR.execute_shell()
