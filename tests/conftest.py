from pytest import fixture


@fixture(scope="function")
def app():
    from .example_app import create_app
    app = create_app()
    with app.app_context():
        yield app


@fixture(scope="function")
def db(app):
    from tests.example_app.models import db
    db.create_all()
    yield db
    db.drop_all()
