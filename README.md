# TDG
[![coverage report](http://gitlab.aengine.com.cn/aengine/tdg/badges/master/coverage.svg)](http://gitlab.aengine.com.cn/aengine/tdg/commits/master)
[![pipeline status](http://gitlab.aengine.com.cn/aengine/tdg/badges/master/pipeline.svg)](http://gitlab.aengine.com.cn/aengine/tdg/commits/master)

## 设计目标

- 降低接口测试维护成本
- 提升接口测试开发效率

## 设计理念

- 数据关系直观
- 无用数据零输入
- 配置优于命令

## 概念

1. 加载模型定义
  
    - `BaseFiller` Model的字段填充器
    - `BaseFillerTypeRepo` 管理Model字段填充器类型仓库
    - `ModelConfig` Model定义对象，其内部包含字段配置的自动填充器
    - `BaseModelConfigParser` ModelConfig的解析器，将Json或其他格式存储的配置解析为ModelConfig实例列表。

2. 解析对象树

    - `ObjNode` 每个待生成的Obj在Tree中都有一个对应的ObjNode对象.
    - `BaseObjTreeParser` 对象树解析器。从Json或其他格式存储的配置中解析需要生成的对象，产出ObjNode列表.
    
3. 组装对象

    - `BaseExplainer` 字段值解释器，以特定的规则去处理字段值。
    - `BaseExplainerRepo` 解释器实例仓库，按照支持的协议管理解释器。
    - `BaseObjBuilder` 对象生成器,配合解释器仓库及填充器仓库将ObjNode创建为实际的数据对象。 

## 对比实例

- 在用例中生成数据的写法

  ```python
  @pytest.fixture(scope="function")
  def obj(app: Flask):
      with app.app_context():
          school_obj = School(name="SSDF", code="SSDF")
          grade_obj = Grade(school=school_obj, name="G01")
          respkg_obj_01 = Respkg(type="prose", name="respkg_01", schools=[school_obj])
          db.session.add(school_obj)
          db.session.add(grade_obj)
          db.session.add(respkg_obj_01)
          db.session.flush()
  
          class_obj = Clas(name="C01", code="C01", grade=grade_obj, respkgs=str(respkg_obj_01.id), teacher_id=1)
          stu_obj = Student(school=school_obj, name="S01", stu_code="S01", gender=0, avatar="https://avatar")
  
          db.session.add(class_obj)
          db.session.add(stu_obj)
          db.session.flush()
  
          stuClas_obj = StudentClas(stu_id=stu_obj.id, cls_id=class_obj.id, finish_reason='')
          art_obj_01 = Article(title="art_title_01", title_py="art_title_py_01", author="art_aut_01",
                               author_py="art_aut_py_01",
                               cover_img="http://cover_01", banner_img="http://banner_01", content="art_con_01",
                               content_py="art_con_py_01", brief="brief_01", brief_py="brief_py_01", note="note_01",
                               note_py="note_py_01",
                               appreciation="app_01", appreciation_py="app_py_01", type="prose", respkgs=[respkg_obj_01])
          art_obj_02 = Article(title="art_title_02", title_py="art_title_py_02", author="art_aut_02",
                               author_py="art_aut_py_02",
                               cover_img="http://cover_02", banner_img="http://banner_02", content="art_con_02",
                               content_py="art_con_py_02", brief="brief_02", brief_py="brief_py_02", note="note_02",
                               note_py="note_py_02",
                               appreciation="app_02", appreciation_py="app_py_02", type="prose", respkgs=[respkg_obj_01])
          art_obj_03 = Article(title="art_title_03", title_py="art_title_py_03", author="art_aut_03",
                               author_py="art_aut_py_03",
                               cover_img="http://cover_03", banner_img="http://banner_03", content="art_con_03",
                               content_py="art_con_py_03", brief="brief_03", brief_py="brief_py_03", note="note_03",
                               note_py="note_py_03",
                               appreciation="app_03", appreciation_py="app_py_03", type="prose", respkgs=[respkg_obj_01])
          db.session.add(stuClas_obj)
          db.session.add(art_obj_01)
          db.session.add(art_obj_02)
          db.session.add(art_obj_03)
          db.session.flush()
  
          read_statu_01 = ReadingStatu(student_id=stu_obj.id, article_id=art_obj_01.id, finished=1, read_finished=1,
                                       pron_finished=1,
                                       answer_finished=1, read_stars=1, pron_stars=2, answer_stars=3, stars=6,
                                       article_type="prose")
          read_statu_02 = ReadingStatu(student_id=stu_obj.id, article_id=art_obj_02.id, finished=0, article_type="prose")
          db.session.add(read_statu_01)
          db.session.add(read_statu_02)
  
          db.session.commit()
          obj = (stu_obj, art_obj_01)
          yield obj
  
          db.session.delete(school_obj)
          db.session.delete(grade_obj)
          db.session.delete(class_obj)
          db.session.delete(stu_obj)
          db.session.delete(stuClas_obj)
          db.session.delete(respkg_obj_01)
          db.session.delete(art_obj_01)
          db.session.delete(art_obj_02)
          db.session.delete(art_obj_03)
          db.session.delete(read_statu_01)
          db.session.delete(read_statu_02)
          db.session.commit()
  ```

- TDG 语法

  ```python
  tdg.gen({
      'model': 'School',
      'alias': 'sch',
      'items': [{
          'model': 'Grade',
          '$school': 'parent>',
          'items': [{
              'model': 'Clas',
              'alias': 'c1',
              '$grade': 'parent>',
              '$respkg': 'calc> lambda rp1: str(rp1.id)',
          }]
      }, {
          'model': 'Student',
          '$school': 'parent>',
          'alias': 's1',
          'items':[{
              'model': 'StudentClas',
              '$student': 'parent>',
              '$cls_id': 'ref> c1.id'
          }, {
              'model': 'ReadingStau',
              '$student': 'parent>',
              'duplicate':[{
                  '$article_id': 'ref>r1.id',
                  '$finished': 1,
                  '$read_finished': 1,
                  '$pron_finished': 1,
                  '$answer_finished': 1,
                  '$pron_stars': 3,
                  '$read_stars': 3,
                  '$answer_stars': 3
              }, {
                  '$article_id': 'ref> r2.id',
                  '$finished': 0,
              }]
          }]
      }, {
          'model': 'Respkg',
          'alias': 'rp1',
          '$schools': 'calc> lambda sch: [sch]',
          'items': [{
              'model': 'Article',
              '$respkgs': 'calc> lambda rp1: [rp1]' ,
              'duplicate':[{
                  'alias': 'r1',
              },{
                  'alias': 'r2',
              },{
                  'alias': 'r3',
              },]
          }]
      }]
  })
  ```

## 语法说明

### 字段说明

| 字段     | 必须 | 描述                                                         |
| -------- | ---- | ------------------------------------------------------------ |
| model    | √    | 声明该条记录的类型．                                         |
| alias    | ×    | 指定该条记录的访问别名．                                     |
| items    | ×    | 该条记录在逻辑上的子项．                                     |
| duplicate    | ×    | 用于批量制定字项，存在该字段时会将当前其他字段作为inst中各记录实例的默认值. |
| $**** | ×    | 传递给Model实例化方法                                        |

### 字段值生成协议

> 针对 DefaultTreeParser

`>` 区分协议与协议值

| 协议     | 协议内容                                             |
| ---------- | -------------------------------------------------------- |
| parent | 父级对象 |
| ref          | 已创建对象的值表达式，如`stu.name`                                       |
| calc      | lambda表达式，参数为tdg中已存在对象的alias                     |

## API说明

### 创建关系数据组

- 创建一条学校记录

    ```python
    tdg.gen({
        'model': 'School',
    })
    ```

- 创建该学校内有一个年级

  ```python
  tdg.gen({
      'model': 'School',
      'items':[{
          'model': 'Grade',
          '$school': 'parent>'
      }]
  })
  ```

### 直接获取object数据

- 依据别名获取obj对象
    
    ```python
    tdg.gen({
        'model': 'School',
        'alias': 's1',
        '$name': 'Aengine学校'
    })
    
    school_obj = tdg['s1']
    assert school_obj.name == 'Aengine学校' # True
    ```

## ChangeLog

- 1.1.0
    
    - `feat` 为字段自动设置默认的填充器。

- 1.0.2
    
    - `fix` gen() can not pass not str values!
