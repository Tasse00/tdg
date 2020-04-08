from typing import List, Type

from flask_sqlalchemy import SQLAlchemy, Model

from tdg import BaseTdg, DefaultFillerTypeRepo, DefaultExplainerRepo, DefaultObjBuilder, DefaultModelConfigRepo, \
    DefaultModelConfigParser
from tdg.v0.tree.default import DefaultObjTreeParser
from tdg.v0.utils import p, ref
from tests.example_app.models import School, Grade, Class, Student


class Tdg(BaseTdg):
    default_filler_type_repo = DefaultFillerTypeRepo()
    default_explainer_repo = DefaultExplainerRepo()
    default_obj_tree_parser = DefaultObjTreeParser()
    default_obj_builder = DefaultObjBuilder()

    def __init__(self, db: SQLAlchemy, models: List[Type[Model]], models_config: dict,
                 auto_clean_when_teardown: bool = True):
        """
        :param db: flask-sqlalchemy 实例
        :param models: Model对象列表，用于自动清理
        :param models_config_desc: 字段填充规则的配置
        :param auto_clean_in_ctx: 上下文使用时，自动清空数据库（不重建）
        """
        model_config_repo = DefaultModelConfigRepo()
        model_config_parser = DefaultModelConfigParser(model_config_repo, self.default_filler_type_repo)
        model_config_parser.parse_and_store(models, models_config)

        super(Tdg, self).__init__(db,
                                  models,
                                  model_config_repo,
                                  self.default_explainer_repo,
                                  self.default_obj_tree_parser,
                                  self.default_obj_builder,
                                  auto_clean_when_teardown)


def test_v0_usage(db):
    """test DefaultObjTreeParser"""

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
    }

    tdg = Tdg(db, [School, Grade, Class, Student], model_config)

    data_to_gen = [{
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
        "name": lambda sch1, grd1: 1000 * sch1.id + 100 * grd1.id
    }]
    tdg.gen(data_to_gen)

    assert isinstance(tdg['sch1'], School)
    assert isinstance(tdg['grd1'], Grade)
    assert isinstance(tdg['cls1'], Class)
    assert isinstance(tdg['stu1'], Student)

    assert tdg['sch1'].name == "Sch01"
    assert tdg['stu1'].school_id == tdg['sch1'].id
    assert tdg['stu1'].grade_id == tdg['grd1'].id
    assert tdg['stu1'].class_id == tdg['cls1'].id
    assert tdg['stu1'].name == str(1000 * tdg['sch1'].id + 100 * tdg['grd1'].id)

    assert School.query.count() == 2
    assert Grade.query.count() == 2
    assert Class.query.count() == 1
    assert Student.query.count() == 1
