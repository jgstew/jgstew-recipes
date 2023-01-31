#!/usr/local/autopkg/python
#
# Copyright 2021 James Stewart @JGStew
#
# This is meant to handle sessions and cookies while downloading.
"""See docstring for URLDownloaderRequests class"""

import os
import pickle

import requests
from autopkglib import Processor, ProcessorError
from autopkglib.URLDownloader import URLDownloader

__all__ = ["URLDownloaderRequests"]


class URLDownloaderRequests(URLDownloader):
    """This is meant to be supplimental to URLDownloader or URLDownloaderPython,
    but use requests to handle sessions / cookies."""

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
        "User_Agent": {
            "required": False,
            "description": ("User Agent Header String to use for download"),
        },
        "disable_ssl_validation": {
            "required": False,
            "default": False,
            "description": "Disables SSL Validation. WARNING: dangerous!",
        },
        "request_method": {
            "required": False,
            "default": "GET",
            "description": "Request Method to use, defaults to GET.",
        },
        "request_headers": {
            "required": False,
            "default": {},
            "description": "Request Headers to use.",
        },
    }
    output_variables = {
        "pathname": {"description": "Path to the downloaded file."},
    }
    __doc__ = description

    def get_requests_session(self) -> requests.Session:
        """get the existing or new session"""
        try:
            return pickle.loads(
                self.env.get("requests_session", pickle.dumps(requests.session()))
            )
        except Exception:
            self.output(
                "WARNING! Could not restore session from previous step. Ressetting to new session."
            )
            return requests.session()

    def main(self):
        """Execution starts here"""

        self.output("WARNING: This is a work in progress!")

        # get previous session:
        requests_session = self.get_requests_session()
        request_headers = self.env.get("request_headers", {})

        # Clear and initiazize data structures
        self.clear_vars()

        url = self.env.get("url", None)
        request_method = self.env.get("request_method", "GET")

        # Ensure existence of necessary files, directories and paths
        filename = self.get_filename()
        if filename is None:
            return

        # in some cases, the filename could have html parameters after:
        if "?" in filename:
            self.output("Removing ? and following characters from filename", 0)
            # this fix should be applied to URLDownloader.prefetch_filename()
            filename = filename.split("?", 1)[0]

        self.env["filename"] = filename
        download_dir = self.get_download_dir()
        self.env["pathname"] = os.path.join(download_dir, filename)

        # clear empty file from previous run
        self.clear_zero_file(self.env["pathname"])

        # prepare request: (need to add options for data and headers)
        req = requests.Request(request_method, url, headers=request_headers)

        prepped = requests_session.prepare_request(req)

        requests_result = requests_session.send(prepped, allow_redirects=True)

        with open(self.env["pathname"], "wb") as f:
            f.write(requests_result.content)

        self.output(requests_result.text, 5)

        # save session to env var for use in next invocation:
        self.env["requests_session"] = pickle.dumps(requests_session)


if __name__ == "__main__":
    PROCESSOR = URLDownloaderRequests()
    PROCESSOR.execute_shell()
