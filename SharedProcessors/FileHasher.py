#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# pylint: disable=C0103
"""See docstring for FileHasher class"""

from hashlib import sha1, sha256, md5
from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,unused-import

__all__ = ["FileHasher"]


class FileHasher(Processor):  # pylint: disable=invalid-name
    """Hashes file at pathname and returns hash metadata."""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": False,
            "description": (
                "Path to hash. Defaults to %pathname%."
            ),
        }
    }
    output_variables = {
        "filehasher_sha1": {
            "description": "The input file SHA1"
        },
        "filehasher_sha256": {
            "description": "The input file SHA256"
        },
        "filehasher_md5": {
            "description": "The input file MD5"
        },
        "filehasher_size": {
            "description": "The input file size"
        }
    }

    __doc__ = description

    def hash(self, file_path):
        """run hashes"""

        # https://github.com/jgstew/bigfix_prefetch/blob/master/url_to_prefetch.py
        hashes = sha1(), sha256(), md5()

        chunksize = max(409600, max(a_hash.block_size for a_hash in hashes))
        size = 0

        file_stream = open(file_path, "rb")

        while True:
            chunk = file_stream.read(chunksize)
            if not chunk:
                break
            # get size of chunk and add to existing size
            size += len(chunk)
            # add chunk to hash computations
            for a_hash in hashes:
                a_hash.update(chunk)

        self.output("File MD5    = {filehasher_md5}".format(
            filehasher_md5=hashes[2].hexdigest()), 1)
        self.output("File SHA1   = {filehasher_sha1}".format(
            filehasher_sha1=hashes[0].hexdigest()), 1)
        self.output("File SHA256 = {filehasher_sha256}".format(
            filehasher_sha256=hashes[1].hexdigest()), 1)
        self.output("File Size   = {filehasher_size}".format(
            filehasher_size=size), 1)

        self.env['filehasher_sha1'] = hashes[0].hexdigest()
        self.env['filehasher_sha256'] = hashes[1].hexdigest()
        self.env['filehasher_md5'] = hashes[2].hexdigest()
        self.env['filehasher_size'] = size

    def main(self):
        """Execution starts here"""

        # I think this gets the pathname value if `file_path` is not specified?
        file_path = self.env.get("file_path", self.env.get("pathname"))

        self.hash(file_path)


if __name__ == "__main__":
    PROCESSOR = FileHasher()
    PROCESSOR.execute_shell()
