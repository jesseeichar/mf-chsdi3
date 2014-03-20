# -*- coding: utf-8 -*-

from sqlalchemy import Text, Integer
from sphinxalchemy.schema import Index, Attribute, ArrayAttribute
from sqlalchemy import create_engine, MetaData


engine = create_engine('sphinx+mysqldb://service-sphinxsearch.dev.bgdi.ch:9312')
metadata = MetaData(bind=engine)

docs = Index('shorten_urls', metadata,
   Attribute('id', Integer),
   Attribute('long_url', Text),
   Attribute('short_url', Text))
