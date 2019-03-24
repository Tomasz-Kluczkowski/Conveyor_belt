from unittest import mock

import pytest
from devtools import debug

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt
from src.domain_models.feeder import Feeder
from src.domain_models.worker import IDLE
from src.domain_models.worker_pair import WorkerPair


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
        assert basic_worker.items == []
        assert basic_worker.state == IDLE

    def test_take_item(self, basic_worker):
        basic_worker.take_item('A')
        assert basic_worker.items == ['A']

        basic_worker.take_item('B')
        assert basic_worker.items == ['A', 'B']

    def test_take_item_does_not_add_duplicates(self, basic_worker):
        basic_worker.take_item('A')
        basic_worker.take_item('A')
        assert basic_worker.items == ['A']

    def test_take_item_does_not_take_not_required(self, basic_worker):
        basic_worker.take_item('Q')
        assert basic_worker.items == []


class TestWorkerPair:
    def test_init(self, worker_factory):
        worker_1 = worker_factory(id_='Tom')
        worker_2 = worker_factory(id_='Mac')
        worker_pair = WorkerPair(workers=[worker_1, worker_2], id_='pair_1')

        assert worker_pair.workers == [worker_1, worker_2]
        assert worker_pair.id == 'pair_1'


class TestConveyorBelt:
    def test_init_default(self, basic_feeder, basic_receiver):
        conveyor_belt = ConveyorBelt(
            feeder=basic_feeder,
            receiver=basic_receiver,
            num_slots=3,
            id_='belt_id'
        )

        assert conveyor_belt.id == 'belt_id'
        assert conveyor_belt.num_slots == 3
        assert len(conveyor_belt.worker_pairs) == 3
        assert conveyor_belt.feeder == basic_feeder
        assert conveyor_belt.receiver == basic_receiver
        assert conveyor_belt.items_on_belt == []

    def test_init_num_pairs(self, basic_feeder, basic_receiver):
        conveyor_belt = ConveyorBelt(
            feeder=basic_feeder,
            receiver=basic_receiver,
            num_slots=3,
            num_pairs=1,
            id_='belt_id'
        )

        assert conveyor_belt.num_slots == 3
        assert len(conveyor_belt.worker_pairs) == 1
        assert conveyor_belt.feeder == basic_feeder
        assert conveyor_belt.receiver == basic_receiver
        assert conveyor_belt.items_on_belt == []

    def test_num_pairs_exceeding_num_slots(self, conveyor_belt_factory):
        with pytest.raises(ValueError) as exception:
            conveyor_belt_factory(num_pairs=10)

        assert exception.value.args == (
            'Improperly configured ConveyorBelt - num_pairs cannot exceed num_slots.',
        )
