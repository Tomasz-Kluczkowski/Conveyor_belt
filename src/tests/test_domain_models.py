from unittest import mock

import pytest

from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.typing_definitions.custom_types import TypeId


@pytest.fixture()
def receiver_factory():
    receiver = Receiver(TypeId('receiver_id'))
    return receiver


class TestFeeder:
    def test_init(self, feeder_factory):
        assert feeder_factory.id == 'feeder_id'
        assert feeder_factory.components == ['A', 'B']

    @mock.patch('uuid.uuid4')
    def test_auto_id(self, mock_uuid4):
        mock_uuid4.return_value = 'uuid_id'
        feeder = Feeder(['A', 'B'])
        assert feeder.id == 'uuid_id'

    def test_repr_method(self, feeder_factory):
        assert str(feeder_factory) == (
            f"<Feeder(id=feeder_id, components=['A', 'B'], feed_func=basic_feed_func)>"
        )

    def test_feed(self, feeder_factory):
        assert feeder_factory.feed() == 1

    @mock.patch('src.domain_models.feeder.random')
    def test_basic_feed(self, mock_random):
        mock_random.choice.side_effect = ['E', 'E', 'A', 'B']
        feeder = Feeder(['A', 'B', 'E'])
        result = []
        for i in range(4):
            result.append(feeder.feed())
        assert result == ['E', 'E', 'A', 'B']


class TestReceiver:
    def test_init(self, receiver_factory):
        assert receiver_factory.id == 'receiver_id'
        assert receiver_factory.received_items == []

    def test_repr_method(self, receiver_factory):
        assert str(receiver_factory) == (
            f'<Receiver(id=receiver_id, received_items=[])>'
        )

    def test_receive(self, receiver_factory):
        receiver_factory.receive('A')
        assert receiver_factory.received_items == ['A']


# class TestWorker:
#     def test_init(self, worker_factory):
#         assert receiver_factory.id == 'receiver_id'
#         assert receiver_factory.received_items == []

    # def test_repr_method(self, receiver_factory):
    #     assert str(receiver_factory) == (
    #         f'<Receiver(id=receiver_id, received_items=[])>'
    #     )
    #
    # def test_receive(self, receiver_factory):
    #     receiver_factory.receive('A')
    #     assert receiver_factory.received_items == ['A']
