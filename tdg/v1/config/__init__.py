import abc
from typing import Type, List, Union

from flask_sqlalchemy import Model

from tdg.v1.filler import BaseFiller, BaseFillerTypeRepo


class ModelConfigError(Exception):
    def __init__(self, msg: str):
        super(ModelConfigError, self).__init__()
        self.message = msg

    def __repr__(self):
        return "<ModelConfigError %s>" % self.message


class ModelFieldConfig:
    """模型字段配置定义"""

    def __init__(self, name: str, filler: BaseFiller):
        self.name = name
        self.filler = filler


class ModelConfig:
    """模型配置定义"""

    def __init__(self, name: str, model: Type[Model], fields_: List[ModelFieldConfig]):
        self.name = name
        self.model = model
        self.fields = fields_


class BaseModelConfigRepo(abc.ABC):

    @abc.abstractmethod
    def store(self, model_conf_list: List[ModelConfig]):
        pass

    @abc.abstractmethod
    def get_model_conf(self, model_conf_name: str) -> ModelConfig:
        pass

    @abc.abstractmethod
    def get_model_conf_list(self) -> List[ModelConfig]:
        pass

class BaseModelConfigParser(abc.ABC):

    def __init__(self, store: BaseModelConfigRepo, filler_type_repo: BaseFillerTypeRepo):
        self.store = store
        self.filler_type_repo = filler_type_repo

    @abc.abstractmethod
    def parse(self, models: List[Type[Model]], model_conf_desc: Union[dict, List[dict]]) -> List[ModelConfig]:
        pass

    def parse_and_store(self, models: List[Type[Model]], models_config: dict):
        self.store.store(self.parse(models, models_config))
