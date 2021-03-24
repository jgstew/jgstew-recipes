#!/usr/local/python
"""
generate_bes_from_template.py

Created by James Stewart (@JGStew) on 2020-03-03.
"""

from __future__ import absolute_import

import os
import datetime
import re

# pylint: disable=line-too-long
import chevron  # pylint: disable=import-error


def generate_content_from_template(template_dict, template_file_path=None):
    """return content string from template"""

    # get template_file_path from template_dict
    if not template_file_path and 'template_file_path' in template_dict:
        template_file_path = template_dict['template_file_path']

    # template_file_path still missing, but required
    if not template_file_path:
        raise ValueError("`template_file_path` not in template_dict and not passed into function")

    # check if template file exists and readable:
    if not os.path.isfile(template_file_path) or not os.access(template_file_path, os.R_OK):
        raise FileNotFoundError(template_file_path)

    return chevron.render(open(template_file_path, 'r'), template_dict)


def write_file_content(file_path, content_string):
    """write content to file"""
    file_stream = open(file_path, "w")
    file_stream.write(content_string)
    file_stream.close()


def generate_bes_from_template(template_dict, template_file_path=None):
    """This function has been renamed to generate_content_from_template"""
    template_dict = get_missing_bes_values(template_dict)
    return generate_content_from_template(template_dict, template_file_path)


def get_missing_bes_values(template_dict):
    """Get missing values that con be inferred for BigFix Content"""
    if 'SourceReleaseDate' not in template_dict:
        template_dict['SourceReleaseDate'] = yyyymmdd()
    if 'x-fixlet-modification-time' not in template_dict:
        template_dict['x-fixlet-modification-time'] = fixlet_modification_time()
    if 'DownloadSize' not in template_dict and 'prefetch' in template_dict and \
            'size' in template_dict['prefetch']:
        # the following assumes if DownloadSize is not provided, then exactly 1 prefetch will be
        #  NOTE: this could sum the size of multiple prefetch statements if an array is given
        #  WARNING: this is a bit fragile. You may need to specify DownloadSize to bypass this
        template_dict['DownloadSize'] = \
            (re.search(r'size[=:](.*?)\s', template_dict['prefetch']).group(1))

    return template_dict


def yyyymmdd(separator="-", date_to_format=datetime.datetime.today()):
    """By default, get YYYY-MM-DD of today in local time zone"""
    return date_to_format.strftime('%Y' + separator + '%m' + separator + '%d')


def fixlet_modification_time(
        date_to_format=datetime.datetime.now(datetime.timezone.utc)
):
    """By default, get the bigfix fixlet format of time of now in UTC
    Example: Tue, 03 Mar 2020 19:37:59 +0000"""
    return date_to_format.strftime('%a, %d %b %Y %H:%M:%S %z')


def main():
    """Only called if this script is run directly"""

    # get template file relative to this script
    template_file_path = (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "TEMPLATE_TASK.bes.mustache")
    )
    template_dict = {
        'template_file_path': template_file_path,
        'Title': 'Example Generated From Template',
        'Description': 'This Task was generated automatically!',
        'Relevance': [
            {'Relevance': """ Comment: Always False */ FALSE \
/* This example doesn't do anything, so it is always false. """},
            {'Relevance': """ TRUE """}
        ],
        'DownloadSize': 9999,
        'SourceID': 'JGStew',
        'prefetch': 'prefetch file.txt',
        'ActionScript':
            """
delete /tmp/file.txt
copy __Download/file.txt /tmp/file.txt
"""
    }
    #print(template_dict)
    #template_dict = get_missing_bes_values(template_dict)
    output_string = generate_bes_from_template(template_dict)
    print(output_string)
    #write_file_content("/tmp/temp.bes", output_string)
    return output_string


# if called directly, then run this example:
if __name__ == '__main__':
    main()
