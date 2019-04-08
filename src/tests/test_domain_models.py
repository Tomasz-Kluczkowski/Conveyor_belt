import pytest

from unittest import mock

from src.domain_models.common import BaseModel
from src.domain_models.factory_floor import FactoryFloor
from src.domain_models.feeder import Feeder
from src.domain_models.worker import IDLE
from src.domain_models.worker_pair import WorkerPair
from src.exceptions.exceptions import FactoryConfigError, FeederConfigError


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
        assert basic_feeder.components == ['A', 'B', 'E']

    def test_feed_single_element_list(self, basic_feeder):
        assert basic_feeder.feed() == 1

    def test_feed_multiple_element_list(self, feeder_factory):
        feeder = feeder_factory(feed_input=[1, 2, 3])
        assert feeder.feed() == 1
        assert feeder.feed() == 2
        assert feeder.feed() == 3

    def test_feed_with_generator(self, feeder_factory):
        feeder = feeder_factory(feed_input=(item for item in [1, 2, 3]))
        assert feeder.feed() == 1
        assert feeder.feed() == 2
        assert feeder.feed() == 3

    def test_feed_not_iterable(self, feeder_factory):

        with pytest.raises(FeederConfigError) as exception:
            feeder_factory(feed_input=True)

        assert exception.value.args == (
            (
                'Unable to iterate over supplied feed_input of type: bool. Please make sure feed_input is an Iterable '
                'or a Sequence.'
            ),
        )

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


class TestFactoryFloor:
    def test_init_default(self, basic_feeder, basic_receiver):
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
            num_slots=3,
            id_='factory_id'
        )

        assert factory_floor.id == 'factory_id'
        assert factory_floor.num_slots == 3
        assert len(factory_floor.worker_pairs) == 3
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 0

    def test_init_num_pairs(self, basic_feeder, basic_receiver):
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
            num_slots=3,
            num_pairs=1,
            id_='factory_id'
        )

        assert factory_floor.num_slots == 3
        assert len(factory_floor.worker_pairs) == 1
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 0

    def test_num_pairs_exceeding_num_slots(self, factory_floor_factory):
        with pytest.raises(FactoryConfigError) as exception:
            factory_floor_factory(num_pairs=10)

        assert exception.value.args == (
            'Improperly configured FactoryFloor - num_pairs cannot exceed num_slots.',
        )

    def test_push_item_to_receiver(self, factory_floor_factory):
        factory_floor: FactoryFloor = factory_floor_factory()
        factory_floor.conveyor_belt.enqueue(1)
        factory_floor.conveyor_belt.enqueue(2)
        factory_floor.conveyor_belt.enqueue(3)
        factory_floor.push_item_to_receiver()
        assert factory_floor.receiver.received_items == [1]
        assert factory_floor.conveyor_belt.size == 2

    def test_push_item_to_receiver_belt_not_full(self, factory_floor_factory):
        factory_floor: FactoryFloor = factory_floor_factory()
        factory_floor.conveyor_belt.enqueue(1)
        factory_floor.conveyor_belt.enqueue(2)
        factory_floor.push_item_to_receiver()
        assert factory_floor.receiver.received_items == []

    def test_add_new_item_to_belt(self, factory_floor_factory, feeder_factory):
        feeder = feeder_factory(feed_input=[1])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)
        factory_floor.add_new_item_to_belt()
        assert factory_floor.conveyor_belt.size == 1
        assert factory_floor.conveyor_belt.dequeue() == 1

    def test_add_new_item_to_belt_no_space_on_belt(self, factory_floor_factory, feeder_factory):
        feeder = feeder_factory(feed_input=[1])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder, num_slots=1, num_pairs=1)
        factory_floor.add_new_item_to_belt()
        factory_floor.add_new_item_to_belt()
        assert factory_floor.conveyor_belt.size == 1
        assert factory_floor.conveyor_belt.dequeue() == 1

    def test_basic_run_belt(self, factory_floor_factory, feeder_factory):
        feeder = feeder_factory(feed_input=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)
        factory_floor.run_belt()
        assert factory_floor.receiver.received_items == [1, 2, 3, 4, 5, 6, 7]

    def test_basic_run_belt_run_out_of_feed_items(self, factory_floor_factory, feeder_factory):
        feeder = feeder_factory(feed_input=[1])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)

        with pytest.raises(FactoryConfigError) as exception:
            factory_floor.run_belt()

        assert exception.value.args == (
            'Insufficient amount of items available in the feed_input of the Feeder. Please check your configuration.',
        )
