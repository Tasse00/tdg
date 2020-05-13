from tdg import Tdg
from tdg.utils.detect import detect_models
from tests.test_pure_sqla.sqla.models import Base, School, Grade, Class, Student


def test_tdg_sqla(session):
    tdg = Tdg(session, detect_models(Base, ["tests/test_pure_sqla/sqla"]))

    data_to_gen = [{
        "model": "School",
        "duplicate": [{
            "alias": "sch1"
        }, {
            "alias": "sch2",
            "$name": "Sch02",
            "items": [{
                "model": "Grade",
                "alias": "grd1",
                "$school": "parent>",
                "items": [{
                    "model": "Class",
                    "alias": "cls1",
                    "$grade": "parent>"
                }]
            }, {
                "model": "Grade",
                "alias": "grd2",
                "$school": "parent>",
            }]
        }]
    }, {
        "model": "Student",
        "alias": "stu1",
        "$id": 1000,
        "$school_id": "ref > sch1.id",
        "$grade_id": "ref > grd1.id",
        "$class_id": "ref > cls1.id",
        "$name": 'calc>lambda sch1, grd1: 1000*sch1.id+100*grd1.id',
        "$hobbies": 'calc>lambda h1, h2: [h1, h2]',
    }, {
        "model": "Hobby",
        "duplicate": [{'alias': 'h1'}, {'alias': 'h2'}],
    }]
    tdg.gen(data_to_gen)

    assert isinstance(tdg['sch1'], School)
    assert isinstance(tdg['grd1'], Grade)
    assert isinstance(tdg['cls1'], Class)
    assert isinstance(tdg['stu1'], Student)

    assert tdg['sch2'].name == "Sch02"
    assert tdg['stu1'].school_id == tdg['sch1'].id
    assert tdg['stu1'].grade_id == tdg['grd1'].id
    assert tdg['stu1'].class_id == tdg['cls1'].id
    assert tdg['stu1'].name == str(1000 * tdg['sch1'].id + 100 * tdg['grd1'].id)

    assert session.query(School).count() == 2
    assert session.query(Grade).count() == 2
    assert session.query(Class).count() == 1
    assert session.query(Student).count() == 1
