#!/usr/local/autopkg/python
"""
BigFixSessionRelevance.py
"""

from autopkglib import Processor, ProcessorError
from besapi import besapi
from BESImport import BESImport


# get relevance for test group membership: concatenations " OR " of ("( exists computer names whose(it as lowercase contains %22autopkg%22) )"; it whose(it as trimmed string != "") | "False") of concatenations " OR " of ("( member of groups " & item 0 of it & " of sites %22ActionSite%22 )") of ((it as string) of ids of it, names of sites of it) of bes computer groups whose(name of it as lowercase contains "autopkg" AND name of it as lowercase contains "test")

__all__ = ["BigFixSessionRelevance"]


class BigFixSessionRelevance(BESImport):
    """AutoPkg Processor to get BigFix Session Relevance Results"""

    description = __doc__
    input_variables = {
        "session_relevance": {
            "required": True,
            "description": "The session relevance to query",
        },
    }
    output_variables = {
        "ses_rel_results": {
            "description": "The results of the session relevance"
        },
    }
    __doc__ = description

    def main(self):
        """BigFixSessionRelevance Main Method"""
        session_relevance = self.env.get("session_relevance")

        self.output(f"\nQ: {session_relevance}")

        # load besapi conf:
        self.get_config()

        BES_USERNAME = self.env.get("BES_USER_NAME")
        BES_PASSWORD = self.env.get("BES_PASSWORD")
        BES_ROOT_SERVER = self.env.get("BES_ROOT_SERVER")

        # clear password from ENV
        self.env["BES_PASSWORD"] = ""

        # BigFix Server Connection
        bes_conn = besapi.BESConnection(
            BES_USERNAME, BES_PASSWORD, BES_ROOT_SERVER, verify=False
        )

        # get results:
        ses_rel_results = bes_conn.session_relevance_string(session_relevance)

        # if verbose, output result:
        self.output(f"\nA: \n{ses_rel_results}")

        # store result:
        self.env["ses_rel_results"] = ses_rel_results



if __name__ == "__main__":
    processor = BigFixSessionRelevance()
    processor.execute_shell()
