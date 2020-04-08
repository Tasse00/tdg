from tdg.v0.tree.default import DefaultObjTreeParser
from tdg.v0.utils import p, ref
from tests.example_app.models import School, Grade, Class, Student


def test_obj_tree_parser():
    """test DefaultObjTreeParser"""
    tree_desc = [{
        "model": School,
        "insts": [{
            "alias": "sch1",
            "name": "Sch01",
            "items": [{
                "alias": "grd1",
                "model": Grade,
                "school": p,
                "items": [{
                    "model": Class,
                    "alias": "cls1",
                    "grade": p,
                }]}, {
                "alias": "grd2",
                "model": Grade,
                "school": p,
            }]
        }, {
            "alias": "sch2",
        }]
    }, {
        "model": Student,
        "alias": "stu1",
        "school_id": ref('sch1').id,
        "grade_id": ref("grd1").id,
        "class_id": ref("cls1").id,
        "name": lambda sch, grd: 1000 * sch.id + 100 * grd.id
    }]

    parser = DefaultObjTreeParser()
    nodes = parser.parse(tree_desc)
    assert [n.alias for n in nodes] == ["sch1", "grd1", "cls1", "grd2", "sch2", "stu1"]
