import pytest

from src.tests.factories import FeederFactory, ReceiverFactory, WorkerFactory


def basic_feed_func():
    return 1  # pragma: no cover


@pytest.fixture()
def feeder_factory():
    return FeederFactory


@pytest.fixture()
def basic_feeder():
    return FeederFactory(feed_func=basic_feed_func)


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
