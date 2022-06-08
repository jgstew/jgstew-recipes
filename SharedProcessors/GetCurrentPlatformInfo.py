#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
#
"""See docstring for GetCurrentPlatformInfo class"""

import math
import platform
import sys

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["GetCurrentPlatformInfo"]


class GetCurrentPlatformInfo(Processor):  # pylint: disable=invalid-name
    """get platform info for system this is running on"""

    description = __doc__
    input_variables = {
        "lowercase_results": {
            "required": False,
            "default": False,
            "description": "make all results lowercase?",
        }
    }
    output_variables = {
        "sys_platform": {"description": ("python sys.platform")},
        "sys_maxsize_bits": {"description": ("python sys.maxsize")},
        "platform_system": {"description": ("python platform.system")},
        "platform_release": {"description": ("python platform.release")},
        "platform_version": {"description": ("python platform.version")},
        "platform_machine": {"description": ("python platform.machine")},
        # "platform_uname": {"description": ("python platform.uname")},
        "platform_processor": {"description": ("python platform.processor")},
        "platform_architecture": {"description": ("python platform.architecture")},
        "platform_platform": {"description": ("python platform.platform")},
        "platform_python_version": {"description": ("python platform.python_version")},
        # "platform_system_alias": {"description": ("python platform.system_alias")},
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        lowercase_results = self.env.get("lowercase_results", False)
        sys_platform = str(sys.platform)
        # sys_maxsize_raw = str(sys.maxsize)
        sys_maxsize_bits = str(int((math.log(int(sys.maxsize)) / math.log(2)) + 1))
        platform_system = str(platform.system())
        platform_release = str(platform.release())
        platform_version = str(platform.version())
        platform_machine = str(platform.machine())
        # platform_uname = str(platform.uname())
        platform_processor = str(platform.processor())
        platform_architecture = str(platform.architecture())
        platform_platform = str(platform.platform(aliased=1))
        platform_python_version = str(platform.python_version())
        # platform_system_alias = str(
        #     platform.system_alias(
        #         platform.system(), platform.release(), platform.version()
        #     )
        # )

        if lowercase_results:
            sys_platform = sys_platform.lower()
            sys_maxsize_bits = sys_maxsize_bits.lower()
            platform_system = platform_system.lower()
            platform_release = platform_release.lower()
            platform_version = platform_version.lower()
            platform_machine = platform_machine.lower()
            # platform_uname = platform_uname.lower()
            platform_processor = platform_processor.lower()
            platform_architecture = platform_architecture.lower()
            platform_platform = platform_platform.lower()
            platform_python_version = platform_python_version.lower()
            # platform_system_alias = platform_system_alias.lower()

        self.env["sys_platform"] = sys_platform
        self.env["sys_maxsize_bits"] = sys_maxsize_bits
        self.env["platform_system"] = platform_system
        self.env["platform_release"] = platform_release
        self.env["platform_version"] = platform_version
        self.env["platform_machine"] = platform_machine
        # self.env["platform_uname"] = platform_uname
        self.env["platform_processor"] = platform_processor
        self.env["platform_architecture"] = platform_architecture
        self.env["platform_platform"] = platform_platform
        self.env["platform_python_version"] = platform_python_version
        # self.env["platform_system_alias"] = platform_system_alias


if __name__ == "__main__":
    PROCESSOR = GetCurrentPlatformInfo()
    PROCESSOR.execute_shell()
