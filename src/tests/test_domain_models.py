import pytest

from unittest import mock

from src.domain_models.common import BaseModel
from src.domain_models.exceptions import InvalidItemOperation
from src.domain_models.feeder import Feeder


class TestBaseModel:
    def test_init(self):
        base_model = BaseModel(id_='base_id')
        assert base_model.id == 'base_id'

    @mock.patch('uuid.uuid4')
    def test_auto_id(self, mock_uuid4):
        mock_uuid4.return_value = 'uuid_id'
        base_model = BaseModel()
        assert base_model.id == 'uuid_id'


class TestFeeder:
    def test_init(self, basic_feeder):
        assert basic_feeder.id == 'feeder_id'
        assert basic_feeder.components == ['A', 'B']

    def test_feed(self, basic_feeder):
        assert basic_feeder.feed() == 1

    @mock.patch('src.domain_models.feeder.random')
    def test_default_feed(self, mock_random):
        mock_random.choice.side_effect = ['E', 'E', 'A', 'B']
        feeder = Feeder(['A', 'B', 'E'])
        result = []
        for i in range(4):
            result.append(feeder.feed())
        assert result == ['E', 'E', 'A', 'B']


class TestReceiver:
    def test_init(self, basic_receiver):
        assert basic_receiver.id == 'receiver_id'
        assert basic_receiver.received_items == []

    def test_receive(self, basic_receiver):
        basic_receiver.receive('A')
        assert basic_receiver.received_items == ['A']


class TestWorker:
    def test_init(self, basic_worker):
        assert basic_worker.id == 'worker_id'
        assert basic_worker.name == 'Tomek'
        assert basic_worker.required_items == ['A', 'B']
        assert basic_worker.left is None
        assert basic_worker.right is None

    def test_take_items(self, basic_worker):
        basic_worker.take_item('A')
        assert basic_worker.left == 'A'

        basic_worker.take_item('B')
        assert basic_worker.right == 'B'

        with pytest.raises(InvalidItemOperation) as exception:
            basic_worker.take_item('C')

        assert exception.value.args == ("Unable to pick up item: 'C'.",)
