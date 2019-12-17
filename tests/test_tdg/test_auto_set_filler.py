from tdg import Tdg
from tests.example_app.models import School, Grade, Class, Student


def test_auto_set_filler(db):
    tdg = Tdg(db, [School, Grade, Class, Student], {})

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
    }]
    tdg.gen(data_to_gen)

    assert isinstance(tdg['sch1'], School)
    assert isinstance(tdg['grd1'], Grade)
    assert isinstance(tdg['cls1'], Class)
    assert isinstance(tdg['stu1'], Student)

    assert tdg['sch2'].name == "Sch02"

    assert School.query.count() == 2
    assert Grade.query.count() == 2
    assert Class.query.count() == 1
    assert Student.query.count() == 1
