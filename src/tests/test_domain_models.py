import pytest

from unittest import mock

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt, ConveyorBeltState
from src.domain_models.factory_floor import FactoryFloor
from src.domain_models.feeder import Feeder
from src.domain_models.worker import WorkerState
from src.exceptions.exceptions import FactoryConfigError, FeederConfigError
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig


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
        feeder = Feeder(('A', 'B', 'E'))
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
        assert basic_worker.state == WorkerState.IDLE
        assert basic_worker.slot_number == 1
        assert basic_worker.operation_times.PICKING_UP == 1
        assert basic_worker.operation_times.DROPPING == 1
        assert basic_worker.operation_times.BUILDING == 4
        assert basic_worker.elapsed_time_of_operation == 0

    def test_take_item(self, basic_worker):
        basic_worker.take_item('A')
        assert basic_worker.items == ['A']

    def test_take_item_does_not_add_duplicates(self, basic_worker):
        basic_worker.take_item('A')
        basic_worker.take_item('A')
        assert basic_worker.items == ['A']

    def test_take_item_does_not_take_not_required(self, basic_worker):
        basic_worker.take_item('Q')
        assert basic_worker.items == []


class TestFactoryFloor:
    def test_init_default(self, basic_feeder, basic_receiver):
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
            id_='factory_id'
        )

        assert factory_floor.id == 'factory_id'
        assert factory_floor.num_pairs == 3
        assert len(factory_floor.workers) == 6
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 0

    def test_init_num_pairs(self, basic_feeder, basic_receiver):
        config = FactoryFloorConfig
        config.NUM_PAIRS = 1
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
            id_='factory_id',
            config=config
        )

        assert len(factory_floor.workers) == 2
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 0

    def test_num_pairs_exceeding_num_slots(self, factory_floor_factory):
        class FactoryTestConfig(FactoryFloorConfig):
            NUM_PAIRS = 10
        config = FactoryTestConfig()
        with pytest.raises(FactoryConfigError) as exception:
            factory_floor_factory(config=config)

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
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder, conveyor_belt__num_slots=1)
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


class TestConveyorBelt:
    def test_initialises_with_all_slots_free(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        assert conveyor_belt.slot_states == {
            0: 'free',
            1: 'free',
            2: 'free',
        }

    def test_check_at_slot_with_item_present(self, conveyor_belt_factory):
        conveyor_belt = conveyor_belt_factory()
        conveyor_belt.enqueue(1)
        assert conveyor_belt.check_at_slot(0) == 1

    def test_check_at_slot_with_item_not_present(self, conveyor_belt_factory):
        conveyor_belt = conveyor_belt_factory()
        assert conveyor_belt.check_at_slot(0) == FactoryFloorConfig.EMPTY

    def test_check_at_slot_with_slot_number_exceeding_maximum_raises_exception(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        with pytest.raises(ValueError) as exception:
            conveyor_belt.check_at_slot(12345)

        assert exception.value.args == (
            "Slot number exceeding conveyor belt's maximum number of slots.",
        )

    def test_set_slot_state_with_slot_number_exceeding_maximum_raises_exception(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        with pytest.raises(ValueError) as exception:
            conveyor_belt.set_slot_state(3, 'test_state')

        assert exception.value.args == (
            "Slot number exceeding conveyor belt's maximum number of slots.",
        )

    def test_set_slot_state(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        conveyor_belt.set_slot_state(2, ConveyorBeltState.BUSY)

        assert conveyor_belt.slot_states == {
            0: 'free',
            1: 'free',
            2: 'busy',
        }

    def test_get_slot_state(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        conveyor_belt.set_slot_state(2, ConveyorBeltState.BUSY)

        assert conveyor_belt.get_slot_state(2) == 'busy'
        assert conveyor_belt.get_slot_state(4) is None

    def test_is_slot_busy(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        conveyor_belt.set_slot_state(2, ConveyorBeltState.BUSY)

        assert conveyor_belt.is_slot_busy(2)
        assert not conveyor_belt.is_slot_busy(1)
        assert not conveyor_belt.is_slot_busy(0)

    def test_is_slot_free(self, conveyor_belt_factory):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory()
        conveyor_belt.set_slot_state(0, ConveyorBeltState.BUSY)
        conveyor_belt.set_slot_state(1, ConveyorBeltState.BUSY)
        conveyor_belt.set_slot_state(2, ConveyorBeltState.FREE)

        assert conveyor_belt.is_slot_free(2)
        assert not conveyor_belt.is_slot_free(1)
        assert not conveyor_belt.is_slot_free(0)
