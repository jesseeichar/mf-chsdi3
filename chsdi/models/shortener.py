# -*- coding: utf-8 -*-

from sqlalchemy import Text, Integer
from sphinxalchemy.schema import Index, Attribute, ArrayAttribute

from chsdi.models import *

Base = bases['shortener']


# https://github.com/Ang3lus/sphinxalchemy
class ShortenUrls(Base):
    __tablename__ = 'shorten_urls'  # The index name
    id = Attribute('id', Integer, primary_key=True)  # Takes the same arguments as sqlalchemy.schema.Column
    long_url = Attribute('long_url', Text)
    short_url = Attribute('short_url', Text)
