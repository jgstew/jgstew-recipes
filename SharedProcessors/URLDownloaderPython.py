#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
"""See docstring for URLDownloaderPython class"""

import os
# import tempfile
import ssl
import json
# import sys

from hashlib import sha1, sha256, md5

# https://stackoverflow.com/questions/3745771/urllib-request-in-python-2-7
from six.moves import urllib

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
        "prefetch_filename": {
            "default": False,
            "required": False,
            "description": (
                "If True, URLDownloader attempts to determine filename from HTTP "
                "headers downloaded before the file itself. 'prefetch_filename' "
                "overrides 'filename' option. Filename is determined from the first "
                "available source of information in this order:\n"
                "\t1. Content-Disposition header\n"
                "\t2. Location header\n"
                "\t3. 'filename' option (if set)\n"
                "\t4. last part of 'url'.  \n"
                "'prefetch_filename' is useful for URLs with redirects."
            ),
        },
        "CHECK_FILESIZE_ONLY": {
            "default": False,
            "required": False,
            "description": (
                "If True, a server's ETag and Last-Modified "
                "headers will not be checked to verify whether "
                "a download is newer than a cached item, and only "
                "Content-Length (filesize) will be used. This "
                "is useful for cases where a download always "
                "redirects to different mirrors, which could "
                "cause items to be needlessly re-downloaded. "
                "Defaults to False."
            ),
        },
        "PKG": {
            "required": False,
            "description": (
                "Local path to the pkg/dmg we'd otherwise download. "
                "If provided, the download is skipped and we just use "
                "this package or disk image."
            ),
        },
        "COMPUTE_HASHES": {
            "required": False,
            "default": True,
            "description": (
                "Local path to the pkg/dmg we'd otherwise download. "
                "If provided, the download is skipped and we just use "
                "this package or disk image."
            ),
        },
        "HEADERS_TO_TEST": {
            "required": False,
            "default": ['ETag', 'Last-Modified', 'Content-Length'],
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
        "url_downloader_summary_result": {
            "description": "Description of interesting results."
        },
    }
    __doc__ = description

    def download_changed(self, headers):
        """Check if downloaded file changed on server."""

        self.output("HTTP Headers: \n{headers}".format(
            headers=headers), 2)

        # get the list of headers to check
        headers_to_test = self.env.get("HEADERS_TO_TEST", None)

        self.output("headers_to_test: {headers_to_test}".format(
            headers_to_test=headers_to_test), 2)

        # get previous info to compare
        previous_download_info = self.get_download_info_json()

        self.output("previous_download_info: \n{previous_download_info}\n".format(
            previous_download_info=previous_download_info), 2)

        header_matches = 0

        try:
            # check Content-Length:
            if 'Content-Length' in headers_to_test and (  # pylint: disable=no-else-return
                int(
                    previous_download_info['http_headers']['Content-Length']
                ) != int(headers.get('Content-Length'))
            ):
                self.output("Content-Length is different", 2)
                return True
            else:
                header_matches += 1
        except Exception as err:  # pylint: disable=broad-except
            self.output("WARNING: 'Content-Length' header missing. \n{err}\n".format(
                err=err)
            )

        try:
            # check other headers:
            for test in headers_to_test:
                if test != 'Content-Length':
                    if previous_download_info['http_headers'][test] != headers.get(test):  # pylint: disable=line-too-long,no-else-return
                        self.output("{test} is different".format(
                            test=test), 2)
                        return True
                    else:
                        header_matches += 1
        except Exception as err:  # pylint: disable=broad-except
            self.output("WARNING: header missing. \n{err}\n".format(
                err=err)
            )

        # if no header checks work without throwing exceptions:
        if header_matches == 0:
            return True
        # if all above pass, then return False:
        return False

    def store_download_info_json(self, download_dictionary):
        """If file is downloaded, store info"""
        pathname = self.env.get("pathname")
        pathname_info_json = pathname + ".info.json"
        # https://stackoverflow.com/questions/16267767/python-writing-json-to-file
        with open(pathname_info_json, "w") as outfile:
            json.dump(download_dictionary, outfile, indent=4)
            # add newline at end of file:
            outfile.write('\n')

    def get_download_info_json(self):
        """get info from previous download"""
        pathname = self.env.get("pathname")
        pathname_info_json = pathname + ".info.json"

        try:
            with open(pathname_info_json, "r") as infile:
                info_json = json.load(infile)
        except Exception as err:  # pylint: disable=broad-except
            self.output("failed to get previous download info: \n{err}\n".format(
                err=err)
            )
            return None

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

    def download_and_hash(self, file_save_path):  # pylint: disable=too-many-branches
        """stream down file from url and calculate size & hashes"""
        # it is much more efficient to calculate hashes WHILE downloading
        # this allows the file to be read only once and never from disk
        # https://github.com/jgstew/bigfix_prefetch/blob/master/src/bigfix_prefetch/prefetch_from_url.py
        url = self.env.get("url")
        download_dictionary = {}

        hashes = None
        if self.env.get("COMPUTE_HASHES", None):
            hashes = sha1(), sha256(), md5()

        # chunksize seems like it could be anything
        #   it is probably best if it is a multiple of a typical hash block_size
        #   a larger chunksize is probably best for faster downloads
        #   chunksize should be evenly divisible by 4096 due to 4k blocks of storage
        chunksize = 4096 * 100
        if hashes:
            chunksize = max(chunksize, max(a_hash.block_size for a_hash in hashes))

        size = 0

        file_save = None

        if file_save_path:
            file_save = open(file_save_path, 'wb')

        # get http headers
        response = urllib.request.urlopen(url, context=self.ssl_context_certifi())
        response_headers = response.info()

        self.env["download_changed"] = self.download_changed(response_headers)
        # check if download changed from last run:
        if not self.env.get("download_changed", None):
            # Discard the temp file
            os.remove(file_save_path)
            return None

        # download file
        while True:
            chunk = response.read(chunksize)
            if not chunk:
                break
            # get size of chunk and add to existing size
            size += len(chunk)
            # add chunk to hash computations
            if hashes:
                for a_hash in hashes:
                    a_hash.update(chunk)
            # save file if handler
            if file_save:
                file_save.write(chunk)

        # close file handler if used
        if file_save:
            file_save.close()

        download_dictionary['file_name'] = self.env.get("filename", "")
        download_dictionary['file_size'] = size
        if hashes:
            download_dictionary['file_sha1'] = hashes[0].hexdigest()
            download_dictionary['file_sha256'] = hashes[1].hexdigest()
            download_dictionary['file_md5'] = hashes[2].hexdigest()
        download_dictionary['download_url'] = url
        #download_dictionary['http_headers'] = response.info()
        try:
            # save http header info to dict
            download_dictionary['http_headers'] = {}
            download_dictionary['http_headers']['Content-Length'] = int(
                response.headers['content-length']
            )
            download_dictionary['http_headers']['ETag'] = response.headers['ETag']
            download_dictionary['http_headers']['Last-Modified'] = response.headers[
                'Last-Modified']
            if download_dictionary['http_headers']['Content-Length'] != size:
                # should this be a halting error?
                self.output("WARNING: file size != content-length header")
        except Exception as err:  # pylint: disable=broad-except
            # probably need to handle a missing header better than this
            self.output("header error: \n{err}\n".format(
                err=err)
            )

        # Save last-modified and etag headers to files xattr
        # This is for backwards compatibility with URLDownloader
        try:
            # this can throw errors on Linux running in WSL
            # it might also throw errors on Linux containers
            self.store_headers(response.info())
        except Exception as err:  # pylint: disable=broad-except
            self.output("xattr error: \n{err}\n".format(
                err=err)
            )

        return download_dictionary

    def main(self):
        """Execution starts here"""
        # Clear and initiazize data structures
        self.clear_vars()

        #self.prefetch_filename()

        # Ensure existence of necessary files, directories and paths
        filename = self.get_filename()
        if filename is None:
            return
        self.env["filename"] = filename
        download_dir = self.get_download_dir()
        self.env["pathname"] = os.path.join(download_dir, filename)

        # clear empty file from previous run
        self.clear_zero_file(self.env["pathname"])

        # change headers to test if CHECK_FILESIZE_ONLY
        if self.env.get("CHECK_FILESIZE_ONLY", None):
            self.env["HEADERS_TO_TEST"] = ['Content-Length']

        pathname_temporary = self.create_temp_file(download_dir)

        # download file
        download_dictionary = self.download_and_hash(pathname_temporary)

        self.output("download_dictionary: \n{download_dictionary}\n".format(
            download_dictionary=download_dictionary), 2)

        if self.env.get("download_changed", None):
            # Move the new temporary download file to the pathname
            self.move_temp_file(pathname_temporary)

        # clear temp file if 0 size
        self.clear_zero_file(pathname_temporary)

        if self.env.get("download_changed", None):
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
