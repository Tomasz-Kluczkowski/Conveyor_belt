from unittest import mock

from src.domain_models.feeder import Feeder
from src.typing_definitions.custom_types import TypeId


class TestFeeder:
    @staticmethod
    def basic_feed_func():
        return 1

    def test_init(self):
        feeder = Feeder(['A', 'B'], self.basic_feed_func, TypeId('feeder_id'))
        assert feeder.id == 'feeder_id'
        assert feeder.components == ['A', 'B']
        assert feeder.feed_func == self.basic_feed_func

    @mock.patch('uuid.uuid4')
    def test_auto_id(self, mock_uuid4):
        mock_uuid4.return_value = 'feeder_id'
        feeder = Feeder(['A', 'B'], self.basic_feed_func)
        assert feeder.id == 'feeder_id'
