import os

from django.db import connections


def init_test_db():
    with connections['realtime'].cursor() as cursor:
        with open(os.path.join('proco', 'realtime_unicef', 'tests', 'db', 'initdb.sql'), 'r') as initdb_file:
            cursor.execute(initdb_file.read())
