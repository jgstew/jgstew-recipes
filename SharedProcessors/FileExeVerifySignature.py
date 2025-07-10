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

    This is a cross platform alternative to `autopkglib/SignToolVerifier`

    Limitation - This should only work for EXE and DLL files (PE Files)

    Example Output:

    com.github.jgstew.SharedProcessors/FileExeVerifySignature
    {'Input': {'file_pathname': 'SoftwareUpdate.exe'}}
    FileExeVerifySignature: No value supplied for file_signature_throw_error, setting default value of: True
    {'Output': {'file_signature_date': '2008-07-25',
                'file_signature_datetime': '2008-07-25 22:21:53+00:00',
                'file_signature_more_info': 'http://www.apple.com/macosx',
                'file_signature_program_name': 'Apple Software Update',
                'file_signature_result': 'VALID',
                'file_signature_result_raw': 'AuthenticodeVerificationResult.OK',
                'file_signature_serial_number': '12451790217711796967571790799059482938',
                'file_signature_valid': True}}

    Related:

    - https://github.com/jgstew/tools/blob/master/Python/get_pefile_signify.py
    - https://stackoverflow.com/a/72520692/861745
    - https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/SignToolVerifier.py
    - https://github.com/NickETH/autopkg/blob/win/Code/autopkglib/WindowsSignatureVerifier.py
    - https://github.com/mtrojnar/osslsigncode
    - https://github.com/sassoftware/relic
    """

    description = __doc__
    input_variables = {
        "file_pathname": {"required": False, "description": "file path to verify"},
        "file_signature_throw_error": {
            "required": False,
            "default": True,
            "description": "Throw error on failed verification?",
        },
        "file_signature_expected_serial_number": {
            "required": False,
            "default": "",
            "description": "Expected serial number for the signature",
        },
        "file_sig_date_custom_output": {
            "required": False,
            "default": "SourceReleaseDate",
            "description": "custom variable to store file_signature_date",
        },
    }
    output_variables = {
        "file_signature_date": {"description": "The date of the signature"},
        "file_signature_datetime": {"description": "The date of the signature"},
        "file_signature_more_info": {"description": "The info of the signature"},
        "file_signature_valid": {"description": "Is the signature valid?."},
        "file_signature_result": {"description": "The result of the validation"},
        "file_signature_result_raw": {"description": "The result of the validation"},
        "file_signature_program_name": {
            "description": "The program_name in the signature."
        },
        "file_signature_serial_number": {"description": "The serial_number"},
    }

    def main(self):
        """execution starts here"""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        file_signature_throw_error = self.env.get("file_signature_throw_error", True)
        file_sig_date_custom_output = str(
            self.env.get("file_sig_date_custom_output", "SourceReleaseDate")
        ).strip()
        file_signature_expected_serial_number = str(
            self.env.get("file_signature_expected_serial_number", "")
        ).strip()
        self.env["file_signature_date"] = ""
        self.env["file_signature_datetime"] = ""
        self.env["file_signature_more_info"] = ""
        self.env["file_signature_result"] = "UnknownError"
        self.env["file_signature_result_raw"] = "UnknownErrorRaw"
        self.env["file_signature_valid"] = False
        self.env["file_signature_program_name"] = ""
        self.env["file_signature_serial_number"] = ""
        file_signature_serial_number = ""
        # https://github.com/jgstew/tools/blob/master/Python/get_pefile_signify_time.py
        if file_pathname:
            with open(file_pathname, "rb") as file_io:
                pefile = SignedPEFile(file_io)

                try:
                    file_signature_serial_number = str(
                        list(pefile.signed_datas)[0].signer_infos[0].serial_number
                    ).strip()
                    self.env["file_signature_serial_number"] = (
                        file_signature_serial_number
                    )
                except Exception:
                    # print(err)
                    pass
                try:
                    signing_time = (
                        list(pefile.signed_datas)[0]
                        .signer_infos[0]
                        .countersigner.signing_time
                    )
                    # print(type(signing_time))
                    self.env["file_signature_datetime"] = str(signing_time)
                    self.env["file_signature_date"] = str(
                        signing_time.strftime("%Y-%m-%d")
                    )
                    self.env[file_sig_date_custom_output] = str(
                        signing_time.strftime("%Y-%m-%d")
                    )
                    self.output_variables[file_sig_date_custom_output] = {
                        "description": "custom variable to store file_signature_date",
                    }
                except Exception:
                    # print(err)
                    pass
                try:
                    self.env["file_signature_program_name"] = str(
                        list(pefile.signed_datas)[0].signer_infos[0].program_name
                    ).strip()
                except Exception:
                    # print(err)
                    pass
                try:
                    self.env["file_signature_more_info"] = str(
                        list(pefile.signed_datas)[0].signer_infos[0].more_info
                    ).strip()
                except Exception:
                    # print(err)
                    pass
                try:
                    sig_result, sig_explain = pefile.explain_verify()
                    # print(sig_result)
                    # print(sig_explain)
                    self.env["file_signature_result_raw"] = str(sig_result)
                    if str(sig_result) == "AuthenticodeVerificationResult.OK":
                        self.env["file_signature_result"] = "VALID"
                        self.env["file_signature_valid"] = True
                    elif str(sig_result) == "AuthenticodeVerificationResult.NOT_SIGNED":
                        self.env["file_signature_result"] = "NOT_SIGNED"
                    else:
                        self.env["file_signature_result"] = (
                            str(sig_result) + ":" + str(sig_explain)
                        )
                except Exception as err:
                    print(err)
                    self.env["file_signature_result"] = "ERROR_NOT_VALID"

                if (
                    file_signature_throw_error
                    and self.env["file_signature_valid"] is False
                ):
                    self.env["stop_processing_recipe"] = True
                    raise ProcessorError(f"Signature Invalid! for `{file_pathname}`")

                # check for matching serial
                if file_signature_expected_serial_number != "":
                    if file_signature_serial_number == "":
                        raise ProcessorError(
                            f"Expected Serial `{file_signature_expected_serial_number}` provided, but no serial number found!"
                        )
                    else:
                        if (
                            file_signature_expected_serial_number
                            != file_signature_serial_number
                        ):
                            raise ProcessorError(
                                f"Expected Serial `{file_signature_expected_serial_number}` but does not match found serial `{file_signature_serial_number}`"
                            )


if __name__ == "__main__":
    PROCESSOR = FileExeVerifySignature()
    PROCESSOR.execute_shell()
