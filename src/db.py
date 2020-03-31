from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import g, _app_ctx_stack
from src.models import Base
from os import environ

from src import config

_ = environ.get

session = scoped_session(
    sessionmaker(autocommit=False, autoflush=True, bind=None),
    scopefunc=_app_ctx_stack.__ident_func__,
)


def init_app(app):
    app.before_request(_before_request)
    app.after_request(_after_request)
    app.teardown_appcontext(_teardown_appcontext)

    engine = create_engine(config.DBSTRING, echo=app.debug)
    session.configure(bind=engine)

    Base.query = session.query_property()


def _before_request():
    g.force_commit = False


def _after_request(response):
    try:
        if getattr(g, 'force_commit', False) or response.status_code < 400:
            session.commit()
        else:
            session.rollback()
    finally:
        session.close()

    return response


def _teardown_appcontext(exception=None):
    try:
        session.remove()
    except Exception:
        pass
