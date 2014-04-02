# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text
from sqlalchemy.types import DateTime

from chsdi.models import bases

Base = bases['clientdata']


class ClientData(Base):
    __tablename__ = 'shorturl'
    __table_args__ = ({'schema': 'chsdi', 'autoload': True})
    url_short = Column('url_short', Text, primary_key=True)
    url = Column('url', Text)
    bgdi_created = Column('bgdi_created', DateTime)
