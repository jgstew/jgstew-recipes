#!/usr/local/autopkg/python
"""
BESImport.py
"""
from __future__ import absolute_import

import os.path

try:
    from ConfigParser import SafeConfigParser
except (ImportError, ModuleNotFoundError):
    from configparser import SafeConfigParser

import lxml
import requests
from autopkglib import Processor, ProcessorError
from besapi import besapi

try:
    requests.packages.urllib3.disable_warnings()
except Exception:
    pass

__all__ = ["BESImport"]


class BESImport(Processor):
    """AutoPkg Processor to import content to BigFix REST API using besapi wrapper"""

    description = __doc__
    input_variables = {
        "bes_file": {
            "required": False,
            "description": "Path to BES XML file for console import.",
        },
        "bes_customsite": {
            "required": False,
            "default": "autopkg",
            "description": "BES console custom site for generated content.",
        },
        "besapi_conf_file": {
            "required": False,
            "description": "file path to load root server config from",
        },
        "bes_taskid": {
            "required": False,
            "description": "Task ID to import (overwrite), performs HTTP PUT.",
        },
    }
    output_variables = {
        "bes_id": {"description": "The returned ID of the bigfix content imported."},
        "bes_import_summary_result": {
            "description": "Description of BigFix import results."
        },
    }
    __doc__ = description

    def get_config(self, conf_file=None):
        """load config info from file"""
        config_path = [
            "/etc/besapi.conf",
            os.path.expanduser("~/besapi.conf"),
            os.path.expanduser("~/.besapi.conf"),
            "besapi.conf",
        ]
        if conf_file:
            config_path.append(conf_file)

        CONFPARSER = SafeConfigParser()
        CONFPARSER.read(config_path)

        if CONFPARSER:
            try:
                self.env["BES_ROOT_SERVER"] = CONFPARSER.get(
                    "besapi", "BES_ROOT_SERVER"
                )
                self.env["BES_USER_NAME"] = CONFPARSER.get("besapi", "BES_USER_NAME")
                self.env["BES_PASSWORD"] = CONFPARSER.get("besapi", "BES_PASSWORD")
            except KeyError as err:
                self.output(err, 0)
                self.env["stop_processing_recipe"] = True

    def get_bes_title(self, bes_file):
        """Get title from bes xml file for bigfix content"""
        with open(bes_file, "rb") as file_handle:
            tree = lxml.etree.parse(file_handle)
            self.env["bes_title"] = tree.xpath(
                "/BES/Task/Title/text() | /BES/Task/Fixlet/text()"
            )[0]

    def main(self):
        """BESImport Main Method"""
        # Assign BES Console Variables
        bes_file = self.env.get("bes_file", self.env.get("content_file_pathname"))

        if not bes_file:
            self.output("Nothing to import", 0)
            return 0

        try:
            self.get_config()
        except BaseException:
            self.output("ERROR: No besapi config loaded, use bescli to create one", 0)
            return None

        self.get_bes_title(bes_file)

        bes_title = self.env.get("bes_title")
        bes_customsite = self.env.get("bes_customsite", "autopkg")
        bes_taskid = self.env.get("bes_taskid", None)

        BES_USERNAME = self.env.get("BES_USER_NAME")
        BES_PASSWORD = self.env.get("BES_PASSWORD")
        BES_ROOT_SERVER = self.env.get("BES_ROOT_SERVER")

        # clear password from ENV
        self.env["BES_PASSWORD"] = ""

        # BES Console Connection
        bes_conn = besapi.BESConnection(
            BES_USERNAME, BES_PASSWORD, BES_ROOT_SERVER, verify=False
        )

        # print( bes_conn.get() )

        # PUT, update task
        if bes_taskid:
            self.output("Searching: '%s' for ID '%s'" % (bes_customsite, bes_taskid))

            task = bes_conn.get("task/custom/%s/%s" % (bes_customsite, bes_taskid))

            if task.request.status_code == 200:
                self.output("Found:[%s] '%s'   " % (bes_taskid, task().Task.Title))

                self.output(
                    "Import(PUT): '%s' to %s/tasks/custom/%s"
                    % (bes_file, BES_ROOT_SERVER, bes_customsite)
                )

                with open(bes_file, "rb") as file_handle:
                    upload_result = bes_conn.put(
                        "task/custom/%s/%s" % (bes_customsite, bes_taskid), file_handle
                    )
                    updated_task = bes_conn.get(
                        "task/custom/%s/%s" % (bes_customsite, bes_taskid)
                    )

                # Read, get, and parse console return
                self.env["bes_id"] = str(upload_result)
                self.output(
                    "Result (%s): [%s] %s    "
                    % (
                        upload_result.request.status_code,
                        str(upload_result),
                        updated_task().Task.Title,
                    )
                )

                # Create summary result data
                self.env["bes_import_summary_result"] = {
                    "summary_text": "The following tasks were imported into BigFix:",
                    "report_fields": ["Task ID", "Task Name", "Site"],
                    "data": {
                        "Task ID": str(upload_result),
                        "Task Name": str(updated_task().Task.Title),
                        "Site": str(bes_customsite),
                    },
                }
            else:
                self.output("Task ID:[%s] not found, skipping." % bes_taskid)
                self.env["bes_id"] = 0

        # POST, create task
        else:
            self.output("Searching: '%s' for '%s'" % (bes_customsite, bes_title))
            tasks = bes_conn.get("tasks/custom/%s" % bes_customsite)

            # only print tasks if verbose=3
            self.output(tasks, 3)

            duplicate_task = False
            for task in tasks().iterchildren():
                if task.Name == bes_title:

                    duplicate_task = True

                    self.output(
                        "Found:[%s] '%s' - %s    "
                        % (task.ID, task.Name, task.get("LastModified"))
                    )

            if not duplicate_task:
                self.output(
                    "Import(POST): '%s' to %s/api/tasks/custom/%s"
                    % (bes_file, BES_ROOT_SERVER, bes_customsite)
                )
                self.output(bes_conn.url("tasks/custom/%s" % bes_customsite))
                upload_result = None

                # Upload task
                with open(bes_file, "rb") as file_handle:
                    upload_result = bes_conn.post(
                        "tasks/custom/%s" % bes_customsite, file_handle
                    )

                self.output(upload_result)

                # Read and parse console return
                self.env["bes_id"] = str(upload_result().Task.ID)
                self.output(
                    "Result (%s): [%s] %s - %s    "
                    % (
                        upload_result.request.status_code,
                        upload_result().Task.ID,
                        upload_result().Task.Name,
                        upload_result().Task.get("LastModified"),
                    )
                )

                # Create summary result data
                self.env["bes_import_summary_result"] = {
                    "summary_text": "The following tasks were imported into BigFix:",
                    "report_fields": ["Task ID", "Task Name", "Site"],
                    "data": {
                        "Task ID": str(upload_result().Task.ID),
                        "Task Name": str(upload_result().Task.Name),
                        "Site": str(bes_customsite),
                    },
                }

            else:
                self.output("Duplicate task, skipping import.", 0)
                self.env["bes_id"] = 0


if __name__ == "__main__":
    processor = BESImport()
    processor.execute_shell()
