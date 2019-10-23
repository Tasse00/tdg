import yaml

from tdg.v1.tree.defautl import DefaultObjTreeParser


def test_obj_tree_parser():
    """test DefaultObjTreeParser"""
    tree_desc = '''
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
        $name: 'calc>lambda sch, grd: 1000*sch.id+100*grd.id'
    '''
    tree_json = yaml.load(tree_desc, yaml.BaseLoader)
    parser = DefaultObjTreeParser()
    nodes = parser.parse(tree_json)
    assert [n.alias for n in nodes] == ["sch1", "grd1", "cls1", "grd2", "sch2", "stu1"]
