#!/usr/local/autopkg/python
#
# James Stewart @JGStew - 2021
#
# Related:
# - https://github.com/jgstew/bigfix_prefetch/blob/master/prefetch_from_dictionary.py
#
"""See docstring for AutoPkgCacheCleanup class"""

import datetime
import pathlib

from autopkglib import (  # pylint: disable=import-error,wrong-import-position,unused-import
    Processor,
    ProcessorError,
)

__all__ = ["AutoPkgCacheCleanup"]


def get_file_mtime(file_path):
    """Get file modification time"""
    return datetime.datetime.fromtimestamp(file_path.stat().st_mtime)


def get_file_age(file_path):
    """get file age interval"""
    return datetime.datetime.today() - get_file_mtime(file_path)


class AutoPkgCacheCleanup(Processor):  # pylint: disable=invalid-name
    """checks that assert_string is within input_string"""

    description = __doc__
    input_variables = {
        "cleanup_max_age_days": {
            "required": False,
            "default": 30,
            "description": "Delete cached downloads older than `cleanup_max_age_days` days",
        },
        "cleanup_min_size_mb": {
            "required": False,
            "default": 2,
            "description": "Delete cached files greater than `cleanup_min_size` size. Defaults to 2. (2MB)",
        },
        "cleanup_empty_files": {
            "required": False,
            "default": True,
            "description": "Delete empty files? Default `True`",
        },
        "cleanup_tmp_files": {
            "required": False,
            "default": True,
            "description": "Delete tmp files older than `cleanup_max_age_days` days? Default `True`",
        },
        "cleanup_cache_all": {
            "required": False,
            "default": False,
            "description": "Cleanup cache for all recipes? Default `False`",
        },
    }
    output_variables = {
        "num_files_deleted": {"description": ("The number of files deleted")},
        "total_cache_size_gb": {
            "description": ("Total size of the download cache in GB.")
        },
    }
    __doc__ = description

    def main(self):
        """Execution starts here"""

        cleanup_max_age_days = int(self.env.get("cleanup_max_age_days", 30))
        cleanup_min_size = int(self.env.get("cleanup_min_size_mb", 2)) * 1024 * 1024
        cleanup_empty_files = bool(self.env.get("cleanup_empty_files", True))
        cleanup_tmp_files = bool(self.env.get("cleanup_tmp_files", True))
        cleanup_cache_all = bool(self.env.get("cleanup_cache_all", True))
        RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR", None)
        num_files_deleted = 0
        total_cache_size = 0

        path_cache = pathlib.Path(RECIPE_CACHE_DIR)
        file_cache_pattern = "downloads/*"

        if cleanup_cache_all:
            path_cache = pathlib.Path(RECIPE_CACHE_DIR).parent
            file_cache_pattern = "*/downloads/*"

        self.output(path_cache.absolute(), 3)

        for file_path in path_cache.glob(file_cache_pattern):
            file_size = file_path.stat().st_size
            total_cache_size = total_cache_size + file_size
            file_age_days = get_file_age(file_path).days

            if cleanup_empty_files and file_size == 0:
                # delete empty files:
                file_path.unlink(missing_ok=True)
                num_files_deleted = num_files_deleted + 1
            else:
                if file_age_days > cleanup_max_age_days:
                    # example tmp filename: tmpadsflsdf
                    if (
                        cleanup_tmp_files
                        and file_path.name.startswith("tmp")
                        and "." not in file_path.name
                    ):
                        # delete old tmp files:
                        file_path.unlink(missing_ok=True)
                        num_files_deleted = num_files_deleted + 1
                    else:
                        if file_size > cleanup_min_size:
                            # delete old files:
                            file_path.unlink(missing_ok=True)
                            num_files_deleted = num_files_deleted + 1

        # make it a string so that it can be used in var substitution:
        self.env["num_files_deleted"] = str(num_files_deleted)
        self.env["total_cache_size_gb"] = round(
            total_cache_size / (1024 * 1024 * 1024), 2
        )


if __name__ == "__main__":
    PROCESSOR = AutoPkgCacheCleanup()
    PROCESSOR.execute_shell()
