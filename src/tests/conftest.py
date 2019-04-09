import pytest

from src.tests.factories import FeederFactory, ReceiverFactory, WorkerFactory, FactoryFloorFactory, ConveyorBeltFactory


@pytest.fixture()
def feeder_factory():
    return FeederFactory


@pytest.fixture()
def basic_feeder():
    return FeederFactory(feed_input=[1])


@pytest.fixture()
def receiver_factory():
    return ReceiverFactory


@pytest.fixture()
def basic_receiver():
    return ReceiverFactory()


@pytest.fixture()
def worker_factory():
    return WorkerFactory


@pytest.fixture()
def basic_worker():
    return WorkerFactory()


@pytest.fixture()
def factory_floor_factory():
    return FactoryFloorFactory


@pytest.fixture()
def conveyor_belt_factory():
    return ConveyorBeltFactory


@pytest.fixture()
def basic_conveyor_belt():
    return ConveyorBeltFactory()
