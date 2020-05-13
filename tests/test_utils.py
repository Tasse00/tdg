from tdg.utils.detect import detect_models
from tests.test_pure_sqla.sqla.models import Base, School, Grade, Class, Student, Hobby


def test_detect_models():
    mdls = set(detect_models(Base, ["tests/test_pure_sqla/sqla"]))
    assert mdls == {School, Grade, Class, Student, Hobby}
