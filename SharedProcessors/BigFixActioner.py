#!/usr/local/autopkg/python
"""
BigFixActioner.py
"""

try:
    from ConfigParser import SafeConfigParser
except (ImportError, ModuleNotFoundError):
    from configparser import SafeConfigParser

import chevron

from autopkglib import Processor, ProcessorError
from besapi import besapi
from BESImport import BESImport


__all__ = ["BigFixActioner"]

# noqa: B950
BES_SourcedFixletAction = """\
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">
    <SourcedFixletAction>
        <SourceFixlet>
            <Sitename>{{bes_customsite}}</Sitename>
            <FixletID>{{bes_id}}</FixletID>
            <Action>{{bes_action}}</Action>
        </SourceFixlet>
        <Target>
            <CustomRelevance>exists computer names whose(it as lowercase contains "autopkg")</CustomRelevance>
        </Target>
        <Settings>
            <PreActionShowUI>false</PreActionShowUI>
            <HasRunningMessage>false</HasRunningMessage>
            <HasTimeRange>false</HasTimeRange>
            <HasStartTime>false</HasStartTime>
            <HasEndTime>true</HasEndTime>
            <EndDateTimeLocalOffset>P5D</EndDateTimeLocalOffset>
            <HasDayOfWeekConstraint>false</HasDayOfWeekConstraint>
            <UseUTCTime>false</UseUTCTime>
            <ActiveUserRequirement>NoRequirement</ActiveUserRequirement>
            <ActiveUserType>AllUsers</ActiveUserType>
            <HasWhose>false</HasWhose>
            <PreActionCacheDownload>true</PreActionCacheDownload>
            <Reapply>true</Reapply>
            <HasReapplyLimit>false</HasReapplyLimit>
            <HasReapplyInterval>true</HasReapplyInterval>
            <ReapplyInterval>PT15M</ReapplyInterval>
            <HasRetry>true</HasRetry>
            <RetryCount>99</RetryCount>
            <RetryWait Behavior="WaitForReboot">PT1H</RetryWait>
            <HasTemporalDistribution>false</HasTemporalDistribution>
            <ContinueOnErrors>true</ContinueOnErrors>
            <PostActionBehavior Behavior="Nothing"></PostActionBehavior>
            <IsOffer>true</IsOffer>
            <AnnounceOffer>true</AnnounceOffer>
            <OfferCategory>AutoPkgTesting</OfferCategory>
            <OfferDescriptionHTML><![CDATA[Offer to test AutoPkg created content]]></OfferDescriptionHTML>
        </Settings>
    </SourcedFixletAction>
</BES>
"""


class BigFixActioner(BESImport):
    """AutoPkg Processor to create a BigFix action from imported content"""

    description = __doc__
    input_variables = {
        "bes_id": {
            "required": False,
            "default": 0,
            "description": "ID of the Fixlet or Task to Action",
        },
        "bes_customsite": {
            "required": False,
            "default": "autopkg",
            "description": "BES console custom site to find the Task or Fixlet within.",
        },
        "bes_action": {
            "required": False,
            "default": "Action1",
            "description": "Which Action to run",
        },
    }
    output_variables = {
        "bes_action_id": {
            "description": "The returned ID of the bigfix action created."
        },
    }
    __doc__ = description

    def main(self):
        """BigFixActioner Main Method"""
        template_dict = {}
        template_dict["bes_id"] = self.env.get("bes_id", 0)
        if template_dict["bes_id"] == 0:
            self.output("Nothing to action.", 0)
        else:
            self.get_config()
            template_dict["bes_customsite"] = self.env.get("bes_customsite", "autopkg")
            template_dict["bes_action"] = self.env.get("bes_action", "Action1")

            BES_USERNAME = self.env.get("BES_USER_NAME")
            BES_PASSWORD = self.env.get("BES_PASSWORD")
            BES_ROOT_SERVER = self.env.get("BES_ROOT_SERVER")

            # clear password from ENV
            self.env["BES_PASSWORD"] = ""

            bes_action_data = chevron.render(BES_SourcedFixletAction, template_dict)

            self.output(bes_action_data, 4)

            # BigFix Server Connection
            bes_conn = besapi.BESConnection(
                BES_USERNAME, BES_PASSWORD, BES_ROOT_SERVER, verify=False
            )

            action_result = bes_conn.post("actions", bes_action_data)

            self.output(action_result, 2)

            self.env["bes_action_id"] = str(action_result().Action.ID)


if __name__ == "__main__":
    processor = BigFixActioner()
    processor.execute_shell()
