from unittest import mock

from src.domain_models.common import BaseModel
from src.domain_models.feeder import Feeder
from src.typing_definitions.custom_types import TypeId


class TestBaseModel:
    def test_init(self):
        base_model = BaseModel(id_=TypeId('base_id'))
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

    def test_repr_method(self, basic_feeder):
        assert str(basic_feeder) == (
            f"<Feeder(id=feeder_id, components=['A', 'B'], feed_func=basic_feed_func)>"
        )

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

    def test_repr_method(self, basic_receiver):
        assert str(basic_receiver) == (
            f'<Receiver(id=receiver_id, received_items=[])>'
        )

    def test_receive(self, basic_receiver):
        basic_receiver.receive('A')
        assert basic_receiver.received_items == ['A']


class TestWorker:
    def test_init(self, basic_worker):
        assert basic_worker.id == 'worker_id'
        assert basic_worker.name == 'Tomek'
        assert basic_worker.left is None
        assert basic_worker.right is None

    def test_repr_method(self, basic_worker):
        assert str(basic_worker) == (
            f"<Worker(id=worker_id, name='Tomek', left=None, right=None)>"
        )
    #
    # def test_receive(self, receiver_factory):
    #     receiver_factory.receive('A')
    #     assert receiver_factory.received_items == ['A']
