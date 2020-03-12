from os import environ
import logging

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

_ = environ.get

SQL_URI = _('SQL_URI',
            'postgresql://untitled-web:untitled-web@localhost/crawler-staging')


logging.basicConfig(format='[%(asctime)s][%(levelname)s]  %(message)s ',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=True, bind=None))
session.configure(bind=create_engine(SQL_URI, convert_unicode=True))
