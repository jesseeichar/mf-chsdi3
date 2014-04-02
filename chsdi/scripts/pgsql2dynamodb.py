# -*- coding: utf-8 -*-

import os
import sys
import optparse
from datetime import date
from optparse import OptionParser
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from chsdi.models.clientdata import ClientData
from chsdi.models.clientdata_dynamodb import get_table


if __name__ == '__main__':

    def parse_date(stringDate):
        try:
            dateInt = map(int, stringDate.split('-'))
            return date(dateInt[0], dateInt[1], dateInt[2])
        except:
            parser.print_help()
            sys.exit(1)

    me = os.path.basename(sys.argv[0])

    epilog = '''Examples:

    Short links can be migrated using a date or date range filter (-d)

    1) Migrate all the links from postgresql to dynmaodb
    buildout/bin/python chsdi/scripts/pgsql2dynamodb.py -d all

    2) Migrate all the links created at a given date
    buildout/bin/python chsdi/scripts/pgsql2dynamodb.py -d 2014-02-20

    3) Migrate all the links in a date interval
    buildout/bin/python chsdi/scripts/pgsql2dynamodb.py -d 2014-02-20 2014-02-23
    \n'''

    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(epilog=epilog)
    parser.add_option('-d', '--date_filter', dest='date_filter', default=None, action='store', help='Filter by date(s)')

    (options, args) = parser.parse_args()

    if options.date_filter == 'all':
        dateFrom = None
        dateTo = None
    elif len(args) == 1:
        dateFrom = parse_date(options.date_filter)
        dateTo = parse_date(args[0])
    elif len(args) > 1:
        parser.print_help()
        sys.exit(1)
    elif options.date_filter:
        dateFrom = parse_date(options.date_filter)
        dateTo = None

    engine = create_engine('postgresql://db1.bgdi.admin.ch:5432/clientdata')
    DBSession = scoped_session(sessionmaker())
    DBSession.configure(bind=engine)
    query = DBSession.query(ClientData)

    # FIXME: Limit to 5 for now
    if dateFrom and dateTo is None:
        query = ClientData.filter_by_date(query, dateFrom).limit(5)
    # FIXME: Limit to 5 for now
    elif dateFrom and dateTo:
        query = ClientData.filter_by_daterange(query, dateFrom, dateTo).limit(5)
    # FIXME: Limit to 5 for now
    # else:
        # Query all

    try:
        table = get_table()
        for q in query:
            print q.url
            # Parse url and clean permalink parameters
            print q.url_short
            table.put_item(data={
                           'url_short': q.url_short,
                           'url': q.url,
                           'timestamp': str(q.bgdi_created)
                           })
    except Exception as e:
        print e
        print 'Last try failed'
        sys.exit(1)
    finally:
        DBSession.close()
