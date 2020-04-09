from tdg import Tdg
from tests.example_app.models import School, Grade, Class, Student, Hobby


def test_normal_usage(db):
    model_config = {
        "School": {
            "fillers": {"name": "RandomString"}
        },
        "Grade": {
            "fillers": {"name": "RandomString"}
        },
        "Class": {
            "fillers": {"name": "RandomString"}
        },
        "Student": {
            "fillers": {
                "name": {
                    "class": "RandomString",
                    "args": ["student-"],
                }
            }
        },
        "Hobby": {
            "fillers": {
                "name": {
                    "class": "Constant",
                    "args": ["HOBBY"]
                }
            }
        }
    }

    tdg = Tdg(db, [School, Grade, Class, Student, Hobby], model_config)

    data_to_gen = [{
        "model": "School",
        "duplicate": [{
            "alias": "sch1"
        },{
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

    assert tdg['h1'].name == 'HOBBY'
    assert tdg['h2'].name == 'HOBBY'

    assert School.query.count() == 2
    assert Grade.query.count() == 2
    assert Class.query.count() == 1
    assert Student.query.count() == 1


def test_lazy_build_nodes(db):
    model_config = {

    }

    tdg = Tdg(db, [School, Grade, Class, Student, Hobby], model_config)

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

    assert School.query.count() == 2
    assert Grade.query.count() == 2
    assert Class.query.count() == 1
    assert Student.query.count() == 1


def test_duplicated_m2m_objs(db):
    model_config = {}

    tdg = Tdg(db, [School, Grade, Class, Student, Hobby], model_config)

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

    tdg['stu1'].hobbies += [tdg['h1']]

    # commit 之后，hobbies自动去重
    # db.session.commit()

    assert len(tdg['stu1'].hobbies) == 3
    assert len(set(tdg['stu1'].hobbies)) == 2

    tdg.clean_db()  # 不应抛出异常
