#-*- utf-8 -*-

from pyramid.view import view_config
import pyramid.httpexceptions as exc

from urlparse import urlparse
import uuid
import time

from chsdi.models.clientdata_dynamodb import get_table


def _add_item(url):
    table = get_table()

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


@view_config(route_name='shorten_redirect')
def shorten_redirect(request):
    url_short = request.matchdict.get('id')
    if url_short is None:
        raise exc.HTTPBadRequest('Please provide an id')
    table = _get_table()
    try:
        url = table.get_item(url_short=url_short).get('url')
    except Exception as e:
        print e
        raise exc.HTTPBadRequest('This short url doesn\'t exist: s.geo.admin.ch/%s ' % url_short)
    raise exc.HTTPFound(location=url)
