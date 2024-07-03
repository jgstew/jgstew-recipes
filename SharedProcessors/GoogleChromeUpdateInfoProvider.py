#!/usr/local/autopkg/python
#
# based upon a script written by JasonWalker
#
# Related:
# - https://github.com/jgstew/jgstew-recipes/blob/main/Test-Recipes/GoogleChromeUpdateInfoProvider.test.recipe.yaml
# - https://github.com/google/omaha/blob/main/doc/ServerProtocolV3.md
# - https://source.chromium.org/chromium/chromium/src/+/main:docs/updater/protocol_3_1.md
# - https://github.com/hjuutilainen/adminscripts/blob/master/chrome-enable-autoupdates.py
# - https://gist.github.com/pudquick/8cd029d0967ee6f5ee353ed5a967f33c
# - https://squirrelistic.com/blog/how_to_download_older_version_of_google_chrome
# - https://github.com/SukkaW/CheckChrome
# - https://source.chromium.org/chromium/chromium/src/+/main:docs/updater/protocol_3_1.md
#
import uuid
import xml.etree.ElementTree

import requests
from autopkglib import Processor, ProcessorError

__all__ = ["GoogleChromeUpdateInfoProvider"]


class GoogleChromeUpdateInfoProvider(Processor):
    """Gets a static url for latest Chrome Download"""

    description = (
        "Provides download information for the latest version of Google Chrome."
    )
    input_variables = {
        "chrome_channel": {
            "required": False,
            "default": "stable",
            "description": "Update channel (e.g., stable, beta, dev).",
        },
        "chrome_os_platform": {
            "required": False,
            "default": "win",
            "description": "Operating system (e.g., win, mac, linux).",
        },
        "chrome_os_arch": {
            "required": False,
            "default": "",
            "description": "Architecture (e.g., x64, x86).",
        },
        "chrome_os_version": {
            "required": False,
            "default": "11.0",
            "description": "Operating system version (e.g., 10.0, 6.2).",
        },
        # "chrome_version": {
        #     "required": False,
        #     "default": "",
        #     "description": "Target Chrome version. Leave empty for the latest available.",
        # },
        "chrome_appid": {
            "required": False,
            "default": "{8A69D345-D564-463C-AFF1-A69D9E530F96}",
            "description": "For MacOS set to `com.google.Chrome`.",
        },
    }
    output_variables = {
        "chrome_package_name": {"description": "Name of the Chrome package."},
        "chrome_package_sha256": {"description": "SHA256 hash of the Chrome package."},
        "chrome_package_size": {"description": "Size of the Chrome package."},
        "chrome_download_urls": {
            "description": "List of download URLs for the Chrome package."
        },
        "url": {"description": "A single download url for the Chrome package."},
    }

    def main(self):
        """Execution starts here"""

        request_id = str(uuid.uuid4()).upper()
        # session_id = str(uuid.uuid4()).upper()

        chrome_channel = self.env.get("chrome_channel")
        chrome_os_platform = self.env.get("chrome_os_platform")
        chrome_os_arch = self.env.get("chrome_os_arch")
        chrome_os_version = self.env.get("chrome_os_version")
        # chrome_version = self.env.get("chrome_version", "")
        chrome_appid = self.env.get("chrome_appid", "")

        # chrome_os_platform must be one of:
        # "android" or "Android": Android.
        # "chromeos" or "ChromeOS" or "Chrome OS": Chrome OS.
        # "chromiumos" or "ChromiumOS" or "Chromium OS": Chromium OS.
        # "dragonfly": DragonFly BSD.
        # "freebsd" or "FreeBSD": FreeBSD.
        # "Fuchsia": Fuchsia.
        # "ios" or "iOS": Apple iOS.
        # "linux" or "Linux": Linux and its derivatives, except as mentioned below.
        # "mac" or "Mac OS X": Apple macOS and its derivatives.
        # "openbsd" or "OpenBSD": OpenBSD.
        # "Solaris": Solaris.
        # "win" or "Windows": Microsoft Windows and its derivatives.
        # "Unknown": Sent by some clients instead of "" when the platform is not recognized.

        # chrome_os_arch must be one of:
        # "arm": ARM
        # "arm64": 64-bit ARM
        # "x86": x86
        # "x86_64": x86-64
        # "x64": x64

        # ------------

        # update_request = f"""<?xml version="1.0" encoding="UTF-8"?>
        # <request protocol="3.0" updater="Omaha" sessionid="{{{session_id}}}"
        #     installsource="update3web-ondemand" requestid="{{{request_id}}}">
        #     <os platform="{os}" version="{os_version}" arch="{arch}" />
        #     <app appid="{{8A69D345-D564-463C-AFF1-A69D9E530F96}}" ap="{arch}-{channel}-statsdef_0" lang="" brand="GCEB">
        #         <updatecheck targetversionprefix="{chrome_version}"/>
        #     </app>
        # </request>"""

        # from: https://gist.github.com/pudquick/8cd029d0967ee6f5ee353ed5a967f33c
        update_request = f"""<?xml version="1.0" encoding="UTF-8"?>
        <request protocol="3.0" requestid="{{{request_id}}}">
            <os platform="{chrome_os_platform}" version="{chrome_os_version}" arch="{chrome_os_arch}" />
            <app appid="{chrome_appid}" ismachine="1" release_channel="{chrome_channel}">
                <updatecheck />
            </app>
        </request>
        """

        update_request_url = "https://tools.google.com/service/update2"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Goog-Update-Interactivity": "fg",
        }

        response = requests.post(
            url=update_request_url, headers=headers, data=update_request, timeout=90
        )
        if not response.ok:
            raise ProcessorError(
                f"Error reported: {response.status_code} : {response.text}"
            )

        content_xml = xml.etree.ElementTree.fromstring(response.content)
        try:
            package_name = content_xml.find(
                "app/updatecheck/manifest/packages/package"
            ).get("name")
            package_sha256 = content_xml.find(
                "app/updatecheck/manifest/packages/package"
            ).get("hash_sha256")
            package_size = content_xml.find(
                "app/updatecheck/manifest/packages/package"
            ).get("size")
        except AttributeError as err:
            self.output(response.text)
            raise err

        urls = [
            url.get("codebase")
            for url in content_xml.findall("app/updatecheck/urls/url")
        ]

        self.env["chrome_package_name"] = package_name
        self.env["chrome_package_sha256"] = package_sha256
        self.env["chrome_package_size"] = package_size
        self.env["chrome_download_urls"] = urls

        # Note, it might make sense to filter the list in a smarter way:
        self.env["url"] = f"{urls[-1]}{package_name}"

        # self.output(
        #     f"\nUpdates found:\nName: {package_name}\nSHA256: {package_sha256}\nSize: {package_size}\nDownload URLs: {urls}"
        # )


if __name__ == "__main__":
    processor = GoogleChromeUpdateInfoProvider()
    processor.execute_shell()
