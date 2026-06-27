#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2026
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/SharedProcessors/FileExeVerifySignature.py
#
"""See docstring for FileExeVerifySignatureCertInfo class"""

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)
from signify.authenticode.signed_pe import SignedPEFile

__all__ = ["FileExeVerifySignatureCertInfo"]


def extract_common_name(distinguished_name):
    """Extract the CN (Common Name) component from an X.509 distinguished name string.

    Args:
        distinguished_name: Full DN string like 'CN=Apple Inc., O=Apple Inc., C=US'

    Returns:
        The Common Name value, or empty string if not present
    """
    marker = "CN="
    start = distinguished_name.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    result = []
    index = start
    while index < len(distinguished_name):
        char = distinguished_name[index]
        # an escaped comma (\,) is part of the value, a bare comma ends it
        if char == "\\" and index + 1 < len(distinguished_name):
            result.append(distinguished_name[index + 1])
            index += 2
            continue
        if char == ",":
            break
        result.append(char)
        index += 1
    return "".join(result).strip()


class FileExeVerifySignatureCertInfo(Processor):  # pylint: disable=invalid-name
    """Extracts Authenticode signing certificate details (signer, issuer, validity, serial, fingerprints) from a Windows PE file without verifying the chain."""

    description = __doc__
    input_variables = {
        "file_pathname": {
            "required": False,
            "description": "Path to the PE file to inspect, defaults to %pathname%",
        },
        "raise_error": {
            "required": False,
            "default": False,
            "description": (
                "If True, raise an error when the file has no signature. Default: False"
            ),
        },
    }
    output_variables = {
        "file_cert_subject": {"description": "Full distinguished name of the signer"},
        "file_cert_subject_cn": {"description": "Common Name of the signer"},
        "file_cert_issuer": {"description": "Full distinguished name of the issuer"},
        "file_cert_issuer_cn": {"description": "Common Name of the issuer"},
        "file_cert_valid_from": {"description": "Certificate validity start datetime"},
        "file_cert_valid_to": {"description": "Certificate validity end datetime"},
        "file_cert_serial_number": {"description": "Certificate serial number"},
        "file_cert_sha1_fingerprint": {"description": "SHA1 fingerprint of the cert"},
        "file_cert_sha256_fingerprint": {
            "description": "SHA256 fingerprint of the cert"
        },
    }
    __doc__ = description

    def find_signer_certificate(self, signed_data):
        """Return the certificate that matches the signer (by serial number).

        Args:
            signed_data: A signify SignedData object

        Returns:
            The matching certificate, or the first available certificate as a fallback
        """
        signer_serial = signed_data.signer_infos[0].serial_number
        for certificate in signed_data.certificates:
            if certificate.serial_number == signer_serial:
                return certificate
        # fallback: first certificate in the set
        return list(signed_data.certificates)[0]

    def main(self):
        """Execution starts here."""
        file_pathname = self.env.get("file_pathname", self.env.get("pathname", None))
        raise_error = bool(self.env.get("raise_error", False))

        # reset outputs to empty defaults:
        for key in self.output_variables:
            self.env[key] = ""

        if not file_pathname:
            raise ProcessorError("No file_pathname provided")

        with open(file_pathname, "rb") as file_io:
            pe_file = SignedPEFile(file_io)
            signed_datas = list(pe_file.signed_datas)

            if not signed_datas:
                message = f"No Authenticode signature found in: {file_pathname}"
                if raise_error:
                    raise ProcessorError(message)
                self.output(f"WARNING: {message}", 0)
                return

            certificate = self.find_signer_certificate(signed_datas[0])

            subject = str(certificate.subject.dn)
            issuer = str(certificate.issuer.dn)
            self.env["file_cert_subject"] = subject
            self.env["file_cert_subject_cn"] = extract_common_name(subject)
            self.env["file_cert_issuer"] = issuer
            self.env["file_cert_issuer_cn"] = extract_common_name(issuer)
            self.env["file_cert_valid_from"] = str(certificate.valid_from)
            self.env["file_cert_valid_to"] = str(certificate.valid_to)
            self.env["file_cert_serial_number"] = str(certificate.serial_number)
            self.env["file_cert_sha1_fingerprint"] = str(certificate.sha1_fingerprint)
            self.env["file_cert_sha256_fingerprint"] = str(
                certificate.sha256_fingerprint
            )

        self.output(
            f"Signed by `{self.env['file_cert_subject_cn']}` "
            f"(issued by `{self.env['file_cert_issuer_cn']}`)"
        )
        self.output(
            f"valid {self.env['file_cert_valid_from']} to {self.env['file_cert_valid_to']}",
            2,
        )


if __name__ == "__main__":
    PROCESSOR = FileExeVerifySignatureCertInfo()
    PROCESSOR.execute_shell()
