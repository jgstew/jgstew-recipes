#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for FileHasher class"""

import os
from hashlib import sha1, sha256, md5
from autopkglib import Processor, ProcessorError

__all__ = ["FileHasher"]

class FileHasher(Processor):
    """Hashes file at pathname and returns hash metadata."""

    description = __doc__
    input_variables = {
        "file_path": {
            "required": False,
            "description": (
                "Path to hash. Defaults to %pathname%."
                "This path may also contain basic globbing characters such as "
                "the wildcard '*', but only the first result will be returned."
            ),
        }
    }
    output_variables = {
        "filehasher_sha1": {
            "description": "The input file SHA1"
        },
        "filehasher_sha256":{
            "description": "The input file SHA256"
        },
        "filehasher_md5":{
            "description": "The input file MD5"
        },
        "filehasher_size":{
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

        f = open(file_path, "rb")

        while True:
            chunk = f.read(chunksize)
            if not chunk:
                break
            # get size of chunk and add to existing size
            size += len(chunk)
            # add chunk to hash computations
            for a_hash in hashes:
                a_hash.update(chunk)

        self.output("File MD5    = {filehasher_md5}".format(filehasher_md5=hashes[2].hexdigest()), 1)
        self.output("File SHA1   = {filehasher_sha1}".format(filehasher_sha1=hashes[0].hexdigest()), 1)
        self.output("File SHA256 = {filehasher_sha256}".format(filehasher_sha256=hashes[1].hexdigest()), 1)
        self.output("File Size   = {filehasher_size}".format(filehasher_size=size), 1)
        if self.env.get('verbose') == 1:
            try:
                self.output("prefetch %s sha1:%s size:%d %s sha256:%s" % ( os.path.basename(file_path), hashes[0].hexdigest(), size, self.env.get('url'), hashes[1].hexdigest()) )
                #print(self.env)
            except:
                pass
        self.env['filehasher_sha1'] = hashes[0].hexdigest()
        self.env['filehasher_sha256'] = hashes[1].hexdigest()
        self.env['filehasher_md5'] = hashes[2].hexdigest()
        self.env['filehasher_size'] = size

    def main(self):
        file_path = self.env.get("file_path", self.env.get("pathname"))

        # clear any pre-exising results
        if 'filehasher_sha1' in self.env:
            del self.env['filehasher_sha1']
        if 'filehasher_sha256' in self.env:
            del self.env['filehasher_sha256']
        if 'filehasher_size' in self.env:
            del self.env['filehasher_size']

        self.hash(file_path)

if __name__ == "__main__":
    PROCESSOR = FileHasher()
    PROCESSOR.execute_shell()
