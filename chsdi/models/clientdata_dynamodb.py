#-*- utf-8 -*-

import pyramid.httpexceptions as exc

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.fields import HashKey, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING


# http://boto.readthedocs.org/en/latest/boto_config_tut.html
def _connect():

    return connect_to_region('us-west-2')


def get_table():

    # url_short is the pkey
    try:
        return Table('shorturls', schema=[
                     HashKey('url_short', data_type=STRING)
                     ], global_indexes=[
                     GlobalAllIndex('url-index', parts=[
                                    HashKey('url', data_type=STRING)
                                    ])
                     ],
                     connection=_connect())
    except Exception as e:
        raise exc.HTTPBadRequest('Error during connection %s' % e)
