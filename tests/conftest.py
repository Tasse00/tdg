from pytest import fixture


@fixture(scope="function")
def db():
    from .example_app import create_app
    app = create_app()
    with app.app_context():
        from .example_app.models import db
        db.create_all()
        yield db
        db.drop_all()
