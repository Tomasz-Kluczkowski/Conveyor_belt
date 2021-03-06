import pytest

from unittest import mock

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt
from src.domain_models.factory_floor import FactoryFloor
from src.domain_models.feeder import Feeder
from src.domain_models.worker import Worker
from src.exceptions.exceptions import FactoryConfigError, FeederConfigError


@pytest.fixture
def worker_operation_times():
    class TestWorkerOperationTimes:
        PICKING_UP = 4
        DROPPING = 4
        BUILDING = 4

    return TestWorkerOperationTimes


class TestBaseModel:
    def test_repr_method(self):
        base_model = BaseModel()
        base_model.some_attribute = 'some value'
        assert base_model.__repr__() == '<BaseModel(some_attribute=some value)>'


class TestFeeder:
    def test_init(self, basic_feeder):
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
        assert basic_receiver.received_items == []

    def test_receive(self, basic_receiver):
        basic_receiver.receive('A')
        assert basic_receiver.received_items == ['A']


class TestWorker:
    def test_init(self, basic_worker):
        assert basic_worker.name == 'Tomek'

    def test_pickups_up_component(self, worker_factory, basic_conveyor_belt):
        basic_conveyor_belt.enqueue('A')
        worker = worker_factory(conveyor_belt=basic_conveyor_belt)
        worker.work()
        assert worker.components == ['A']

    def test_cannot_pickup_up_component_if_slot_used_by_another_worker(self, worker_factory, basic_conveyor_belt):
        basic_conveyor_belt.put_item_in_slot(slot_number=0, item='A')
        worker = worker_factory(conveyor_belt=basic_conveyor_belt)
        worker.work()
        assert worker.components == []

    def test_ignores_component_if_the_same(self, worker_factory, basic_conveyor_belt):
        worker = worker_factory(conveyor_belt=basic_conveyor_belt)

        for i in range(2):
            basic_conveyor_belt.enqueue('A')
            basic_conveyor_belt.dequeue()
            worker.work()

        assert worker.components == ['A']

    def test_completes_pickup_operation_in_correct_time(
            self, worker_factory, basic_conveyor_belt: ConveyorBelt, worker_operation_times
    ):
        basic_conveyor_belt.enqueue('A')
        worker = worker_factory(
            conveyor_belt=basic_conveyor_belt,
            operation_times=worker_operation_times
        )

        for i in range(worker_operation_times.PICKING_UP):
            worker.work()

        assert basic_conveyor_belt.is_slot_free(slot_number=0)

    def test_creates_product(self, worker_factory, basic_conveyor_belt):
        worker: Worker = worker_factory(conveyor_belt=basic_conveyor_belt)

        feed_items = ['A', 'B', 'E', 'E', 'E', 'E']
        for feed_item in feed_items:
            basic_conveyor_belt.enqueue(feed_item)
            basic_conveyor_belt.dequeue()
            worker.work()
        assert worker.components == ['P']

    def test_drops_product(self, worker_factory, basic_conveyor_belt):
        worker: Worker = worker_factory(conveyor_belt=basic_conveyor_belt)

        feed_items = ['A', 'B', 'E', 'E', 'E', 'E', 'E']
        for feed_item in feed_items:
            basic_conveyor_belt.enqueue(feed_item)
            basic_conveyor_belt.dequeue()
            worker.work()
        assert worker.components == []

    def test_completes_drop_product_operation_in_correct_time(
            self, worker_factory, basic_conveyor_belt, worker_operation_times
    ):
        worker_operation_times.PICKING_UP = 1
        worker = worker_factory(
            conveyor_belt=basic_conveyor_belt,
            operation_times=worker_operation_times
        )

        feed_items = ['A', 'B', 'E', 'E', 'E', 'E']
        for feed_item in feed_items:
            basic_conveyor_belt.enqueue(feed_item)
            basic_conveyor_belt.dequeue()
            worker.work()
        assert worker.components == ['P']

        for i in range(worker_operation_times.DROPPING):
            worker.work()

        assert worker.components == []
        assert basic_conveyor_belt.is_slot_free(slot_number=0)

    def test_cannot_drop_product_if_slot_is_used_by_another_worker(self, worker_factory, basic_conveyor_belt):
        worker: Worker = worker_factory(conveyor_belt=basic_conveyor_belt)

        feed_items = ['A', 'B', 'E', 'E', 'E', 'E']
        for feed_item in feed_items:
            basic_conveyor_belt.enqueue(feed_item)
            basic_conveyor_belt.dequeue()
            worker.work()

        basic_conveyor_belt.put_item_in_slot(slot_number=0, item='A')
        worker.work()

        assert worker.components == ['P']


class TestFactoryFloor:
    def test_init_default(self, basic_feeder, basic_receiver):
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
        )

        assert factory_floor.num_pairs == 3
        assert len(factory_floor.workers) == 6
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 3

    def test_init_num_pairs(self, basic_feeder, basic_receiver, factory_floor_config):
        factory_floor_config.num_pairs = 1
        factory_floor = FactoryFloor(
            feeder=basic_feeder,
            receiver=basic_receiver,
            config=factory_floor_config
        )

        assert len(factory_floor.workers) == 2
        assert factory_floor.feeder == basic_feeder
        assert factory_floor.receiver == basic_receiver
        assert factory_floor.conveyor_belt.size == 3

    def test_num_pairs_exceeding_num_slots(self, factory_floor_factory, factory_floor_config):
        factory_floor_config.num_pairs = 10
        with pytest.raises(FactoryConfigError) as exception:
            factory_floor_factory(config=factory_floor_config)

        assert exception.value.args == (
            'Improperly configured FactoryFloor - num_pairs cannot exceed num_slots.',
        )

    def test_push_item_to_receiver(self, factory_floor_factory):
        factory_floor: FactoryFloor = factory_floor_factory()
        [factory_floor.conveyor_belt.dequeue() for _ in range(3)]
        [factory_floor.conveyor_belt.enqueue(i) for i in range(3)]
        factory_floor.push_item_to_receiver()
        assert factory_floor.receiver.received_items == [0]
        assert factory_floor.conveyor_belt.size == 2

    def test_add_new_item_to_belt(self, factory_floor_factory, feeder_factory, factory_floor_config):
        feeder = feeder_factory(feed_input=[1])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)
        factory_floor.conveyor_belt.dequeue()
        factory_floor.add_new_item_to_belt()
        assert factory_floor.conveyor_belt.size == 3
        assert [factory_floor.conveyor_belt.dequeue() for i in range(3)] == [
            factory_floor_config.empty_code,
            factory_floor_config.empty_code,
            1
        ]

    def test_basic_run_belt(self, factory_floor_factory, feeder_factory, factory_floor_config):
        feeder = feeder_factory(feed_input=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)
        factory_floor.run()
        assert factory_floor.receiver.received_items == [
            factory_floor_config.empty_code,
            factory_floor_config.empty_code,
            factory_floor_config.empty_code,
            1,
            2,
            3,
            4,
            5,
            6,
            7
        ]

        assert factory_floor.time == 10

    def test_basic_run_belt_run_out_of_feed_items(self, factory_floor_factory, feeder_factory):
        feeder = feeder_factory(feed_input=[1])
        factory_floor: FactoryFloor = factory_floor_factory(feeder=feeder)

        with pytest.raises(FactoryConfigError) as exception:
            factory_floor.run()

        assert exception.value.args == (
            'Insufficient amount of items available in the feed_input of the Feeder. Please check your configuration.',
        )

    def test_run_factory_one_product_created_by_worker_on_slot_zero(
            self, factory_floor_factory, feeder_factory, factory_floor_config
    ):
        factory_floor_config.num_steps = 11
        feeder = feeder_factory(
            feed_input=['A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        )
        factory_floor: FactoryFloor = factory_floor_factory(
            config=factory_floor_config,
            feeder=feeder
        )
        factory_floor.run()
        assert factory_floor.receiver.received_items == ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P', 'E']

    def test_run_factory_two_products_created_by_workers_on_slot_zero(
            self, factory_floor_factory, feeder_factory, factory_floor_config
    ):
        factory_floor_config.num_steps = 13
        feeder = feeder_factory(
            feed_input=['A', 'B', 'A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        )
        factory_floor: FactoryFloor = factory_floor_factory(
            config=factory_floor_config,
            feeder=feeder
        )
        factory_floor.run()
        assert factory_floor.receiver.received_items == [
            'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P', 'E', 'P', 'E'
        ]

    def test_run_factory_three_products_created_by_workers_on_slot_zero_and_first_at_slot_one(
            self, factory_floor_factory, feeder_factory, factory_floor_config
    ):
        factory_floor_config.num_steps = 15
        feeder = feeder_factory(
            feed_input=['A', 'B', 'A', 'B', 'A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        )
        factory_floor: FactoryFloor = factory_floor_factory(
            config=factory_floor_config,
            feeder=feeder
        )
        factory_floor.run()
        assert factory_floor.receiver.received_items == [
            'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P', 'E', 'P', 'E', 'P', 'E'
        ]

    def test_run_factory_worker_ignores_item_not_required(
            self, factory_floor_factory, feeder_factory, factory_floor_config
    ):
        factory_floor_config.num_steps = 13
        factory_floor_config.num_pairs = 1
        feeder = feeder_factory(
            feed_input=['A', 'A', 'A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
        )
        factory_floor: FactoryFloor = factory_floor_factory(
            config=factory_floor_config,
            feeder=feeder
        )
        factory_floor.run()
        assert factory_floor.receiver.received_items == [
            'E', 'E', 'E', 'E', 'E', 'A', 'E', 'E', 'E', 'E', 'E', 'P', 'E'
        ]


class TestConveyorBelt:
    def test_initialization(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)

        assert conveyor_belt.slot_states == {
            0: 'free',
            1: 'free',
            2: 'free',
        }
        assert conveyor_belt.size == 3
        assert conveyor_belt.items == [factory_floor_config.empty_code for i in range(3)]

    def test_check_item_at_slot_with_item_present(self, conveyor_belt_factory):
        conveyor_belt = conveyor_belt_factory()
        conveyor_belt.enqueue(1)

        assert conveyor_belt.check_item_at_slot(0) == 1

    def test_check_item_at_slot_with_item_not_present(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt = conveyor_belt_factory(config=factory_floor_config)

        assert conveyor_belt.check_item_at_slot(0) == factory_floor_config.empty_code

    def test_put_item_in_slot_adds_item_and_sets_slot_to_busy(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.put_item_in_slot(slot_number=0, item='A')

        assert conveyor_belt.check_item_at_slot(slot_number=0) == 'A'
        assert conveyor_belt.is_slot_busy(slot_number=0)

    def test_confirm_operation_finished_changes_slot_state_to_free(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.put_item_in_slot(slot_number=0, item='A')

        assert conveyor_belt.is_slot_busy(slot_number=0)
        conveyor_belt.confirm_operation_at_slot_finished(slot_number=0)
        assert not conveyor_belt.is_slot_busy(slot_number=0)

    def test_is_slot_busy_returns_true(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.put_item_in_slot(slot_number=0, item='A')

        assert conveyor_belt.is_slot_busy(0)

    def test_is_slot_busy_returns_false(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)

        assert not conveyor_belt.is_slot_busy(0)

    def test_is_slot_empty_returns_true(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)

        assert conveyor_belt.is_slot_empty(0)

    def test_is_slot_empty_returns_false(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.enqueue('A')

        assert not conveyor_belt.is_slot_empty(0)

    def test_is_slot_free_returns_true(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        assert conveyor_belt.is_slot_free(slot_number=0)

    def test_is_slot_free_returns_false(self, conveyor_belt_factory, factory_floor_config):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.put_item_in_slot(slot_number=0, item='A')

        assert not conveyor_belt.is_slot_free(slot_number=0)

    def test_retrieve_item_from_slot(
            self, conveyor_belt_factory, factory_floor_config
    ):
        conveyor_belt: ConveyorBelt = conveyor_belt_factory(config=factory_floor_config)
        conveyor_belt.enqueue('A')

        assert conveyor_belt.retrieve_item_from_slot(slot_number=0) == 'A'
        assert conveyor_belt.is_slot_busy(slot_number=0)
        assert conveyor_belt.check_item_at_slot(slot_number=0) == factory_floor_config.empty_code
