from typing import List, Dict, Type

from flask_sqlalchemy import Model
from sqlalchemy import Column, Integer, String, BigInteger, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute

from tdg.v1.config import BaseModelConfigRepo, ModelConfig, BaseModelConfigParser, ModelConfigError, ModelFieldConfig


class DefaultModelConfigRepo(BaseModelConfigRepo):

    def __init__(self):
        self._store: Dict[str, ModelConfig] = {}

    def store(self, model_conf_list: List[ModelConfig]):
        self._store.update({
            model_conf.name: model_conf
            for model_conf in model_conf_list
        })

    def get_model_conf(self, model_conf_name: str) -> ModelConfig:
        return self._store[model_conf_name]

    def get_model_conf_list(self) -> List[ModelConfig]:
        return list(self._store.values())


class DefaultModelConfigParser(BaseModelConfigParser):

    def is_column_need_filler(self, col: Column):
        return not (col.autoincrement == True or col.default or col.nullable or col.server_default)

    def get_column_default_filler(self, col: Column):
        return self.filler_type_repo.create_filler(
            {
                Integer: "IncrNumber",
                String: "RandomString",
                BigInteger: "IncrNumber",
                Text: "RandomString",
                DateTime: "DateTime",
                JSON: "Constant",
                Boolean: "BooleanValue",
            }[col.type.__class__], [], {})

    def parse(self, models: List[Type[Model]], models_conf: dict) -> List[ModelConfig]:
        """
        模型定义格式
        {
            # 模型名称，在models中需存在同名模型
            "ModelName": {
                # 定义字段的填充类型
                "fillers": {
                    # 使用默认参数的StringRandom填充器
                    "field_a": "StringRandom",

                    # 使用 args, kwargs指定填充器材参数
                    "field_b": {
                        "class": "RandomInt",
                        "args": [0, 100],
                        "kwargs": {
                            "other_param": "value"
                        }
                    }
                }
            }
        }
        """
        model_config_list = []

        models = models.copy()

        for model_name, model_conf in models_conf.items():
            mdl_idx = [mdl.__name__ for mdl in models].index(model_name)

            if mdl_idx < 0:
                raise ModelConfigError(f"model_conf['{model_name}'] not exist in models.")

            mdl = models.pop(mdl_idx)
            fillers_cnf = []
            for field_name, filler_conf in model_conf.get('fillers', {}).items():
                if isinstance(filler_conf, str):
                    filler_class = filler_conf
                    args = []
                    kwargs = {}
                else:
                    filler_class = filler_conf['class']  # must existed
                    args = filler_conf.get('args', [])
                    kwargs = filler_conf.get('kwargs', {})

                filler = self.filler_type_repo.create_filler(filler_class, args, kwargs)

                fillers_cnf.append(ModelFieldConfig(
                    name=field_name,
                    filler=filler
                ))

            for attr in dir(mdl):
                if attr in model_conf.get('fillers', {}).keys():
                    continue
                if attr.startswith("_") or attr in ['query']:
                    continue
                model_col = getattr(mdl, attr)
                if not isinstance(model_col, InstrumentedAttribute) or isinstance(model_col.comparator,
                                                                                  RelationshipProperty.Comparator):
                    continue
                col = next(iter(model_col.proxy_set))

                if self.is_column_need_filler(col):
                    filler = self.get_column_default_filler(col)
                    fillers_cnf.append(ModelFieldConfig(
                        attr,
                        filler
                    ))
            mdl_cnf = ModelConfig(name=model_name, model=mdl, fields_=fillers_cnf)
            model_config_list.append(mdl_cnf)

        for rest_model in models:
            fillers_cnf = []
            for attr in dir(rest_model):
                if attr.startswith("_") or attr in ['query']:
                    continue
                model_col = getattr(rest_model, attr)
                if not isinstance(model_col, InstrumentedAttribute) or isinstance(model_col.comparator,
                                                                                  RelationshipProperty.Comparator):
                    continue
                col = next(iter(model_col.proxy_set))
                if self.is_column_need_filler(col):
                    filler = self.get_column_default_filler(col)
                    fillers_cnf.append(ModelFieldConfig(
                        attr,
                        filler
                    ))
            mdl_cnf = ModelConfig(name=rest_model.__name__, model=rest_model, fields_=fillers_cnf)
            model_config_list.append(mdl_cnf)
        return model_config_list
