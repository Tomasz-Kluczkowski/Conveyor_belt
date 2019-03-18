import factory

from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker


class FeederFactory(factory.Factory):
    class Meta:
        model = Feeder
    id_ = 'feeder_id'
    components = ['A', 'B']


class ReceiverFactory(factory.Factory):
    class Meta:
        model = Receiver
    id_ = 'receiver_id'


class WorkerFactory(factory.Factory):
    class Meta:
        model = Worker
    id_ = 'worker_id'
    name = 'Tomek'
    required_items = ['A', 'B']
