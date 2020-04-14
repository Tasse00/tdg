from tdg import Tdg
from tests.example_app.models import School


def test_teardown(db):
    model_config = {}

    tdg = Tdg(db, [School], model_config)

    data_to_gen = [{"model": "School"}]

    tdg.gen(data_to_gen)

    tdg.teardown()

    assert all([f.filler.index == 0 for f in tdg.model_conf_repo.get_model_conf('School').fields])
