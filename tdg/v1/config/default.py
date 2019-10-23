from pprint import pformat
from typing import List, Dict, Union, Type

from flask_sqlalchemy import Model
from marshmallow import Schema, fields, ValidationError

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


class FieldConfSchema(Schema):
    name = fields.String(required=True)
    filler = fields.String(required=True)
    args = fields.Raw()


class ModelConfSchema(Schema):
    name = fields.String(required=True)
    fields = fields.Nested(FieldConfSchema, many=True, required=True)


class DefaultModelConfigParser(BaseModelConfigParser):

    def parse(self, models: List[Type[Model]], model_conf_desc: Union[dict, List[dict]]) -> List[ModelConfig]:

        model_config_list = []
        try:
            models_conf = ModelConfSchema(many=True).load(model_conf_desc)  # typing: List[dict]
        except ValidationError as e:
            raise ModelConfigError(pformat(e.messages))

        models = models.copy()

        for raw_mdl_cnf in models_conf:
            mdl_idx = [mdl.__name__ for mdl in models].index(raw_mdl_cnf['name'])

            if mdl_idx < 0:
                raise ModelConfigError(f"model_conf['{raw_mdl_cnf['name']}'] not exist in models.")
            mdl = models.pop(mdl_idx)
            fields_cnf = []
            for raw_field_cnf in raw_mdl_cnf['fields']:
                raw_arg = raw_field_cnf.get('args', {})
                args, kwargs = ([], raw_arg) if isinstance(raw_arg, dict) else (raw_arg, {})

                filler = self.filler_type_repo.create_filler(raw_field_cnf['filler'], args, kwargs)

                fields_cnf.append(ModelFieldConfig(
                    name=raw_field_cnf['name'],
                    filler=filler
                ))

            mdl_cnf = ModelConfig(name=raw_mdl_cnf['name'], model=mdl, fields_=fields_cnf)
            model_config_list.append(mdl_cnf)

        # if len(models) > 0:
        #     raise ModelConfigError("some model not configure: " + "".join(m.__name__ for m in models))

        return model_config_list
