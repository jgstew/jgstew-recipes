#!/usr/local/autopkg/python
#
# based upon a script written by JasonWalker
#
# Related:
# - https://github.com/hjuutilainen/adminscripts/blob/master/chrome-enable-autoupdates.py
# - https://gist.github.com/pudquick/8cd029d0967ee6f5ee353ed5a967f33c
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
        # "chrome_channel": {
        #     "required": False,
        #     "default": "stable",
        #     "description": "Update channel (e.g., stable, beta, dev).",
        # },
        "chrome_os": {
            "required": False,
            "default": "win",
            "description": "Operating system (e.g., win, mac, linux).",
        },
        # "chrome_arch": {
        #     "required": False,
        #     "default": "x64",
        #     "description": "Architecture (e.g., x64, x86).",
        # },
        "chrome_os_version": {
            "required": False,
            "default": "10.0",
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

        # channel = self.env.get("chrome_channel")
        os = self.env.get("chrome_os")
        # arch = self.env.get("chrome_arch")
        os_version = self.env.get("chrome_os_version")
        # chrome_version = self.env.get("chrome_version", "")
        chrome_appid = self.env.get("chrome_appid", "")

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
                <os platform="{os}" version="{os_version}" />
                <app appid="{chrome_appid}">
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
        self.env["url"] = urls[-1]

        # self.output(
        #     f"\nUpdates found:\nName: {package_name}\nSHA256: {package_sha256}\nSize: {package_size}\nDownload URLs: {urls}"
        # )


if __name__ == "__main__":
    processor = GoogleChromeUpdateInfoProvider()
    processor.execute_shell()
