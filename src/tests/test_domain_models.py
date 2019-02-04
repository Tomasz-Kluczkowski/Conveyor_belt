from unittest import mock

import pytest

from src.domain_models.feeder import Feeder
from src.typing_definitions.custom_types import TypeId


def basic_feed_func():
    return 1


@pytest.fixture()
def feeder_factory():
    feeder = Feeder(['A', 'B'], basic_feed_func, TypeId('feeder_id'))
    return feeder


class TestFeeder:
    def test_init(self, feeder_factory):
        assert feeder_factory.id == 'feeder_id'
        assert feeder_factory.components == ['A', 'B']
        assert feeder_factory.feed_func == basic_feed_func

    @mock.patch('uuid.uuid4')
    def test_auto_id(self, mock_uuid4):
        mock_uuid4.return_value = 'feeder_id'
        feeder = Feeder(['A', 'B'], basic_feed_func)
        assert feeder.id == 'feeder_id'

    def test_feeder_repr_method(self, feeder_factory):
        assert str(feeder_factory) == (
            f"<Feeder(id=feeder_id, components=['A', 'B'], feed_func=basic_feed_func)>"
        )
