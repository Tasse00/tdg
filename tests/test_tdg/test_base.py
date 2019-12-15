import pytest
import yaml

from tdg.v1.builder.default import DefaultObjBuilder
from tdg.v1.config.default import DefaultModelConfigParser, DefaultModelConfigRepo
from tdg.v1.explainer.default import DefaultExplainerRepo
from tdg.v1.filler.default import DefaultFillerTypeRepo
from tdg.v1.tdg import BaseTdg
from tdg.v1.tree.default import DefaultObjTreeParser


def test_error_data(db):
    from tests.example_app.models import School, Grade, Class, Student

    model_config_desc = '''
    School:      # 表名
      fillers:           # 字段填充定义
        name:  # 字段名
          class: RandomString
          args:
            prefix: school-
    Grade:
      fillers:           # 字段填充定义
        name:    # 字段名
          class: RandomString
          args:
            prefix: grade-
    Class:
      fillers:
        name:
          class: RandomString
          args:
            prefix: class-
    Student:
      fillers:
        name: RandomString
    '''

    obj_tree_desc = '''
      - model: School
        duplicate:
          - alias: sch1
            $name1: Sch01
            items:
              - alias: grd1
                model: Grade
                $school: parent>
                items:
                  - model: Class
                    alias: cls1
                    $grade: parent>
              - alias: grd2
                model: Grade
                $school: parent>
          - alias: sch2
      # sch->grd1>cls1>grd2>sch2
      # TreeParser.parse -> List[Node]
      - alias: stu1
        model: Student
        $school_id: ref>sch1.id
        $grade_id: ref>grd1.id
        $class_id: ref>cls1.id
        $name: 'calc>lambda sch1, grd1: 1000*sch1.id+100*grd1.id'
    '''

    model_config_store = DefaultModelConfigRepo()
    filler_type_repo = DefaultFillerTypeRepo()

    DefaultModelConfigParser(
        model_config_store,
        filler_type_repo
    ).parse_and_store(
        [School, Grade, Class, Student],
        yaml.load(model_config_desc, yaml.BaseLoader)
    )
    explainer_repo = DefaultExplainerRepo()

    obj_tree_parser = DefaultObjTreeParser()
    obj_builder = DefaultObjBuilder()

    with BaseTdg(db, model_config_store, explainer_repo, obj_tree_parser, obj_builder) as tdg:

        with pytest.raises(TypeError):
            obj_tree_desc = yaml.load(obj_tree_desc, yaml.BaseLoader)
            tdg.gen(obj_tree_desc)




def test_base_tdg_with_default_coms(db):
    from ..example_app.models import School, Grade, Class, Student

    model_config_desc = '''
    School:      # 表名
      fillers:           # 字段填充定义
        name:  # 字段名
          class: RandomString
          args:
            prefix: school-
    Grade:
      fillers:           # 字段填充定义
        name:    # 字段名
          class: RandomString
          args:
            prefix: grade-
    Class:
      fillers:
        name:
          class: RandomString
          args:
            prefix: class-
    Student:
      fillers:
        name: RandomString
    '''

    obj_tree_desc = '''
      - model: School
        duplicate:
          - alias: sch1
            $name: Sch01
            items:
              - alias: grd1
                model: Grade
                $school: parent>
                items:
                  - model: Class
                    alias: cls1
                    $grade: parent>
              - alias: grd2
                model: Grade
                $school: parent>
          - alias: sch2
      # sch->grd1>cls1>grd2>sch2
      # TreeParser.parse -> List[Node]
      - alias: stu1
        model: Student
        $school_id: ref>sch1.id
        $grade_id: ref>grd1.id
        $class_id: ref>cls1.id
        $name: 'calc>lambda sch1, grd1: 1000*sch1.id+100*grd1.id'
    '''

    model_config_store = DefaultModelConfigRepo()
    filler_type_repo = DefaultFillerTypeRepo()

    DefaultModelConfigParser(
        model_config_store,
        filler_type_repo
    ).parse_and_store(
        [School, Grade, Class, Student],
        yaml.load(model_config_desc, yaml.BaseLoader)
    )
    explainer_repo = DefaultExplainerRepo()

    obj_tree_parser = DefaultObjTreeParser()
    obj_builder = DefaultObjBuilder()

    with BaseTdg(db, model_config_store, explainer_repo, obj_tree_parser, obj_builder) as tdg:
        obj_tree_desc = yaml.load(obj_tree_desc, yaml.BaseLoader)
        tdg.gen(obj_tree_desc)

        assert isinstance(tdg['sch1'], School)
        assert isinstance(tdg['grd1'], Grade)
        assert isinstance(tdg['cls1'], Class)
        assert isinstance(tdg['stu1'], Student)

        assert School.query.count() == 2
        assert Grade.query.count() == 2
        assert Class.query.count() == 1
        assert Student.query.count() == 1

    assert School.query.count() == 0
    assert Grade.query.count() == 0
    assert Class.query.count() == 0
    assert Student.query.count() == 0
