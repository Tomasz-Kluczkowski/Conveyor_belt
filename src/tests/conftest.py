import pytest

from src.tests.factories import FeederFactory


def basic_feed_func():
    return 1  # pragma: no cover


@pytest.fixture()
def feeder_factory():
    feeder = FeederFactory(feed_func=basic_feed_func)
    return feeder
