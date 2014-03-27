#-*- utf-8 -*-

from pyramid.view import view_config
import pyramid.httpexceptions as exc

from urlparse import urlparse
import uuid
import time

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.fields import HashKey, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING


# http://boto.readthedocs.org/en/latest/boto_config_tut.html
def _connect():

    return connect_to_region('us-west-2')


def _get_table():

    # url_short is the pkey
    return Table('shorturls', schema=[
                 HashKey('url_short', data_type=STRING)
                 ], global_indexes=[
                 GlobalAllIndex('url-index', parts=[
                                HashKey('url', data_type=STRING)
                                ])
                 ],
                 connection=_connect())


def _add_item(url):
    try:
        table = _get_table()
    except Exception as e:
        # Mail connection error?
        print e
        raise exc.HTTPBadRequest('Error during connection %s' % e)

    # First try to determine whether url is stored in DynamoDB
    entry = table.query(url__eq=url, index='url-index')
    url_short = None
    for e in entry:
        url_short = e['url_short']
    if url_short:
        return url_short
    # Create a new short url if url not in DB
    url_short = str(uuid.uuid4())
    try:
        table.put_item(data={
                       'url_short': url_short,
                       'url': url,
                       'timestamp': time.strftime('%Y-%m-%d %X', time.localtime())
                       })
    except Exception as e:
        # Mail item addition error?
        print e
        raise exc.HTTPBadRequest('Error during put item %s' % e)
    return url_short


def _check_url(url):
    # We should also check permalink parameters..
    if url is None:
        raise exc.HTTPBadRequest('The parameter url is missing from the request')
    hostname = urlparse(url).hostname
    if hostname is None:
        raise exc.HTTPBadRequest('Could not determine the hostname')
    domain = ".".join(hostname.split(".")[-2:])
    if 'admin.ch' not in domain and 'swisstopo.ch' not in domain and 'bgdi.ch' not in domain:
        raise exc.HTTPBadRequest('Shortener can only be used for admin.ch, swisstopo.ch and bgdi.ch domains')
    return url


@view_config(route_name='shorten', renderer='jsonp')
def shortener(request):
    url = _check_url(
        request.params.get('url')
    )
    url_short = _add_item(url)
    return {
        'shortUrl': ''.join((
                            's.geo.admin.ch/',
                            url_short
                            ))
    }


#@view_config(route_name='shorten_redirect')
# def shorten_redirect(request):
