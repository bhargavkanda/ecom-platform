#!/usr/bin/env python
import os
import sys

from psycopg2.extensions import register_adapter

from zap_apps.zap_commons.adapters import Int4NumericRange, TypedNumericRangeAdapter

if os.environ.get('ZAPENV') == 'STAGING':
    if not any('settings' in i for i in sys.argv ):
        val = raw_input("Are you sure not to use '--settings=zapyle_new.settings.env' [Y/n]")
        if val == 'n' or val == 'N':
            raise Exception('Please select --settings')


if __name__ == "__main__":
    register_adapter(Int4NumericRange, TypedNumericRangeAdapter)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zapyle_new.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
