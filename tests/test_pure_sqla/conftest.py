import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.test_pure_sqla.sqla.models import Base


@pytest.fixture(scope="function")
def session():
    dbfile = "test_sqla.db"
    if os.path.exists(dbfile):
        os.remove(dbfile)
    engine = create_engine("sqlite:///" + dbfile)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    yield Session()

    os.remove(dbfile)
