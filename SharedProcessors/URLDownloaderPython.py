#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for URLDownloaderPython class"""

import os
# import tempfile
import ssl
import json

from hashlib import sha1, sha256, md5

try:
    from urllib.request import urlopen  # Python 3
except ImportError:
    from urllib2 import urlopen  # Python 2

import certifi  # pylint: disable=import-error

from autopkglib import Processor, ProcessorError  # pylint: disable=import-error,wrong-import-position,unused-import
from autopkglib.URLDownloader import URLDownloader  # pylint: disable=import-error


__all__ = ["URLDownloaderPython"]


class URLDownloaderPython(URLDownloader):  # pylint: disable=invalid-name
    """This is meant to be a pure python replacement for URLDownloader
    See: https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/URLDownloader.py
    """

    description = __doc__
    input_variables = {
        "url": {"required": True, "description": "The URL to download."},
        "download_dir": {
            "required": False,
            "description": (
                "The directory where the file will be downloaded to. Defaults "
                "to RECIPE_CACHE_DIR/downloads."
            ),
        },
        "filename": {
            "required": False,
            "description": "Filename to override the URL's tail.",
        },
        "PKG": {
            "required": False,
            "description": (
                "Local path to the pkg/dmg we'd otherwise download. "
                "If provided, the download is skipped and we just use "
                "this package or disk image."
            ),
        },
    }
    output_variables = {
        "pathname": {"description": "Path to the downloaded file."},
        "last_modified": {
            "description": "last-modified header for the downloaded item."
        },
        "etag": {"description": "etag header for the downloaded item."},
        "download_changed": {
            "description": (
                "Boolean indicating if the download has changed since the "
                "last time it was downloaded."
            )
        },
    }
    __doc__ = description

    def prefetch_filename(self):  # pylint: disable=no-self-use
        """Attempt to find filename in HTTP headers."""
        # need to implement this
        return False

    def download_changed(self):  # pylint: disable=no-self-use
        """Check if downloaded file changed on server."""
        # need to implement this - always True for now.
        return True

    def store_download_info_json(self, download_dictionary):
        """If file is downloaded, store info"""
        pathname = self.env.get("pathname")
        pathname_info_json = pathname + ".info.json"
        # https://stackoverflow.com/questions/16267767/python-writing-json-to-file
        with open(pathname_info_json, "w") as outfile:
            json.dump(download_dictionary, outfile, indent=4)
            # add newline at end of file:
            outfile.write('\n')
        return None

    def get_download_info_json(self):
        """get info from previous download"""
        pathname = self.env.get("pathname")
        pathname_info_json = pathname + ".info.json"

        with open(pathname_info_json, "r") as infile:
            info_json = json.load(infile)

        return info_json

    def ssl_context_ignore(self):  # pylint: disable=no-self-use
        """ssl context - ignore SSL validation"""
        # this doesn't need to be a class method
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.output("WARNING: disabling SSL validation is insecure!!!")
        return ctx

    def ssl_context_certifi(self):  # pylint: disable=no-self-use
        """ssl context using certifi CAs"""
        # this doesn't need to be a class method
        # https://stackoverflow.com/questions/24374400/verifying-https-certificates-with-urllib-request
        return ssl.create_default_context(cafile=certifi.where())

    def download_and_hash(self, file_save_path):
        """stream down file from url and calculate size & hashes"""
        # https://github.com/jgstew/bigfix_prefetch/blob/master/src/bigfix_prefetch/prefetch_from_url.py
        url = self.env.get("url")
        download_dictionary = {}
        hashes = sha1(), sha256(), md5()
        # chunksize seems like it could be anything
        #   it is probably best if it is a multiple of a typical hash block_size
        #   a larger chunksize is probably best for faster downloads
        chunksize = max(384000, max(a_hash.block_size for a_hash in hashes))
        size = 0

        file_save = None

        if file_save_path:
            file_save = open(file_save_path, 'wb')

        # start download process:
        response = urlopen(url, context=self.ssl_context_certifi())

        self.output("HTTP Headers: \n{headers}".format(
            headers=response.info()), 2)

        while True:
            chunk = response.read(chunksize)
            if not chunk:
                break
            # get size of chunk and add to existing size
            size += len(chunk)
            # add chunk to hash computations
            for a_hash in hashes:
                a_hash.update(chunk)
            # save file if handler
            if file_save:
                file_save.write(chunk)

        # close file handler if used
        if file_save:
            file_save.close()

        download_dictionary['file_name'] = self.get_filename()
        download_dictionary['file_size'] = size
        download_dictionary['file_sha1'] = hashes[0].hexdigest()
        download_dictionary['file_sha256'] = hashes[1].hexdigest()
        download_dictionary['file_md5'] = hashes[2].hexdigest()
        download_dictionary['download_url'] = url
        #download_dictionary['http_headers'] = response.info()
        download_dictionary['http_Content-Length'] = int(response.headers['content-length'])
        download_dictionary['http_ETag'] = response.headers['ETag']
        download_dictionary['http_Last-Modified'] = response.headers['Last-Modified']

        # Save last-modified and etag headers to files xattr
        self.store_headers(response.info())

        return download_dictionary

    def main(self):
        """Execution starts here"""
        # Clear and initiazize data structures
        self.clear_vars()

        # Ensure existence of necessary files, directories and paths
        filename = self.get_filename()
        if filename is None:
            return
        download_dir = self.get_download_dir()
        self.env["pathname"] = os.path.join(download_dir, filename)
        pathname_temporary = self.create_temp_file(download_dir)

        previous_download_info = self.get_download_info_json()

        self.output("previous_download_info: \n{previous_download_info}\n".format(
            previous_download_info=previous_download_info), 2)

        download_dictionary = self.download_and_hash(pathname_temporary)

        self.output("download_dictionary: \n{download_dictionary}\n".format(
            download_dictionary=download_dictionary), 2)

        if self.download_changed():
            self.env["download_changed"] = True
        else:
            # Discard the temp file
            os.remove(pathname_temporary)
            return

        # New resource was downloaded. Move the temporary download file to the pathname
        self.move_temp_file(pathname_temporary)

        # store download info for checking for existing download
        self.store_download_info_json(download_dictionary)

        # Generate output messages and variables
        self.output(f"Downloaded {self.env['pathname']}")
        self.env["url_downloader_summary_result"] = {
            "summary_text": "The following new items were downloaded:",
            "data": {"download_path": self.env["pathname"]},
        }

        self.output("self.env: \n{self_env}\n".format(
            self_env=self.env), 4)


if __name__ == "__main__":
    PROCESSOR = URLDownloaderPython()
    PROCESSOR.execute_shell()
