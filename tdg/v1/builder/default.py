from typing import List, Dict, Tuple

from flask_sqlalchemy import Model, SQLAlchemy

from tdg.v1.builder import BaseObjBuilder
from tdg.v1.config import BaseModelConfigRepo
from tdg.v1.explainer import BaseExplainerRepo
from tdg.v1.tree import ObjNode


class DefaultObjBuilder(BaseObjBuilder):

    def _get_node_parent_path(self,
                              existed_models: Dict[str, Model],
                              new_alias_models: Dict[str, Model],
                              curr_node: ObjNode) -> List[Model]:
        models: List[Model] = []

        parent = curr_node.parent
        while parent:
            parent_model = new_alias_models.get(parent.alias) or existed_models.get(parent.alias)
            models.append(parent_model)
            parent = parent.parent
        return models

    def _get_requested_objs(self,
                            existed_models: Dict[str, Model],
                            new_alias_models: Dict[str, Model],
                            alias_list: List[str]) -> Dict[str, Model]:
        return {
            alias: new_alias_models.get(alias) or existed_models.get(alias)
            for alias in alias_list
        }

    def build(self, db: SQLAlchemy,
              model_conf_repo: BaseModelConfigRepo,
              explainer_repo: BaseExplainerRepo,
              existed_objs: Dict[str, Model],
              nodes: List[ObjNode]) -> Tuple[Dict[str, Model], List[Model]]:
        """flush至db"""
        new_alias_models: Dict[str, Model] = {}
        total_objs = []  # 考虑到重alias obj
        for node in nodes:
            # 可能会获取出错,需要反馈给使用者: Model配置不对
            model_cnf = model_conf_repo.get_model_conf(node.model)
            alias = node.alias
            values = node.values

            auto_filled_fields = {field.name: field.filler.next() for field in model_cnf.fields}

            user_specified_fields = {}
            for field_name, field_desc in values.items():

                if field_desc.protocol:
                    explainer = explainer_repo.get_explainer(field_desc.protocol)

                    parents_path = self._get_node_parent_path(existed_objs,
                                                              new_alias_models,
                                                              node)
                    field_value = explainer.get_value(parents_path,
                                                      self._get_requested_objs(existed_objs,
                                                                               new_alias_models,
                                                                               explainer.need_objs(field_desc.expr)),
                                                      field_desc.expr)
                    user_specified_fields[field_name] = field_value
                else:
                    user_specified_fields[field_name] = field_desc.expr

            auto_filled_fields.update(user_specified_fields)

            # 暂不处理异常
            obj = model_cnf.model(**auto_filled_fields)
            db.session.add(obj)
            db.session.flush()

            new_alias_models[alias] = obj
            total_objs.append(obj)
        db.session.commit()
        return new_alias_models, total_objs