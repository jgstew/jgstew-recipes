#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
#
"""See docstring for GetCommonPlatformEnumeration class"""

import os.path

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["GetCommonPlatformEnumeration"]


class GetCommonPlatformEnumeration(Processor):  # pylint: disable=invalid-name
    """Infer likely CPE from recipe metadata or provided override values"""

    description = __doc__
    input_variables = {
        "cpe_product": {
            "required": False,
            "default": "",
            "description": "value to override cpe product",
        },
        "cpe_vendor": {
            "required": False,
            "default": "",
            "description": "value to override cpe vendor",
        },
        "cpe_target_sw": {
            "required": False,
            "default": "",
            "description": "value to override cpe target_sw",
        },
        "cpe_target_hw": {
            "required": False,
            "default": "",
            "description": "value to override cpe target_hw",
        },
    }
    output_variables = {
        "cpe": {"description": ("the env var to store the result")},
    }
    __doc__ = description

    def get_parent_folder_name(self):
        """Gets the recipe parent folder name"""

        recipe_dir = self.env.get("RECIPE_DIR", "")

        parent_folder_name = os.path.basename(recipe_dir)

        return parent_folder_name

    def sanitize_text_cpe_part(self, input_string):
        """sanitize input_string to be cpe compliant"""
        # lower case:
        input_string = str(input_string).lower()
        # replace certain special characters:
        input_string = input_string.replace(" ", "_").replace("-", "_")
        input_string = input_string.replace(":", r"\:")

        return input_string

    def get_env_version(self):
        """get version from env vars"""

        exclude_vars = ["AUTOPKG_VERSION", "MinimumVersion"]

        for item in self.env:
            # get any env var with version in name:
            if "version" in str(item).lower():
                # exclude known other version vars:
                if str(item) not in exclude_vars:
                    return self.sanitize_text_cpe_part(self.env[item])
        return "0.0.0"

    def get_env_product_name(self):
        """infer product name from metadata"""

        env_var_check_order = ["TitleName", "DisplayName", "NAME"]

        for item_check in env_var_check_order:
            for item in self.env:
                if str(item) == item_check:
                    return self.sanitize_text_cpe_part(self.env[item])

        return "unknown_product"

    def get_env_target_sw(self):
        """infer target_sw from env"""

        target_sw = "*"
        # template_file_path is best (should work even in overrides / children)
        # tail of RECIPE_PATH is recipe file name
        # tail of RECIPE_CACHE_DIR is identifier by default

        template_file_path = self.env.get("template_file_path", "")

        if template_file_path != "":
            if "linux" in str(template_file_path).lower():
                target_sw = "linux"
            if "mac" in str(template_file_path).lower():
                target_sw = "macos"
            if "win" in str(template_file_path).lower():
                target_sw = "windows"

        return self.sanitize_text_cpe_part(target_sw)

    def get_env_target_hw(self):
        """infer target_hw from metadata"""

        # default target_hw:
        target_hw = "*"
        if "64BitOnly" in self.env:
            target_hw = "x64"
        if "32BitOnly" in self.env:
            target_hw = "x32"

        return self.sanitize_text_cpe_part(target_hw)

    def get_cpe(self):
        """primary function"""

        cpe_product = self.env.get("cpe_product", "")
        cpe_vendor = self.env.get("cpe_vendor", "")
        cpe_target_sw = self.env.get("cpe_target_sw", "")
        cpe_target_hw = self.env.get("cpe_target_hw", "")
        version = self.env.get("version", "")

        if cpe_vendor == "":
            cpe_vendor = self.sanitize_text_cpe_part(self.get_parent_folder_name())

        if cpe_product == "":
            # infer cpe_product from TitleName or DisplayName or Name
            cpe_product = self.get_env_product_name()

        if version == "":
            # infer version from env var with name containing `version`
            version = self.get_env_version()

        if cpe_target_sw == "":
            cpe_target_sw = self.get_env_target_sw()

        if cpe_target_hw == "":
            cpe_target_hw = self.get_env_target_hw()

        cpe = (
            "cpe:2.3:a"
            + f":{cpe_vendor}:{cpe_product}:{version}:"
            + "*:*:*:*"
            + f":{cpe_target_sw}:{cpe_target_hw}:*"
        )

        return cpe

    def main(self):
        """Execution starts here"""
        # References:
        # - https://cpe.mitre.org/specification/
        # - https://en.wikipedia.org/wiki/Common_Platform_Enumeration

        cpe = self.env.get("cpe", "")

        # only get and define CPE if it doesn't already exist
        if cpe == "":
            cpe = self.get_cpe()
            self.env["cpe"] = cpe
        else:
            self.output("INFO: cpe already defined.")


if __name__ == "__main__":
    PROCESSOR = GetCommonPlatformEnumeration()
    PROCESSOR.execute_shell()
