#!/usr/local/autopkg/python
#
# Copyright 2021 James Stewart @JGStew
#
# Latest Code is found here: https://github.com/jgstew/autopkg/blob/dev/Code/autopkglib/URLDownloaderPython.py
# This is now just a stub that points to that
"""See docstring for URLDownloaderPython class"""

import autopkglib.URLDownloaderPython  # pylint: disable=import-error
from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["URLDownloaderPython"]


class URLDownloaderPython(autopkglib.URLDownloaderPython):
    """This is meant to be a pure python replacement for URLDownloader
    See: https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/URLDownloader.py
    Latest Code is found here: https://github.com/jgstew/autopkg/blob/dev/Code/autopkglib/URLDownloaderPython.py
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
            "default": False,
            "description": (
                "Local path to the pkg/dmg we'd otherwise download. "
                "If provided, the download is skipped and we just use "
                "this package or disk image."
            ),
        },
        "HEADERS_TO_TEST": {
            "required": False,
            "default": ["ETag", "Last-Modified", "Content-Length"],
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


if __name__ == "__main__":
    PROCESSOR = URLDownloaderPython()
    PROCESSOR.execute_shell()
