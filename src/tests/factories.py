import factory

from src.domain_models.factory_floor import FactoryFloor
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker


class FeederFactory(factory.Factory):
    class Meta:
        model = Feeder
    id_ = 'feeder_id'
    components = ['A', 'B', 'E']


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


class ConveyorBeltFactory(factory.Factory):
    class Meta:
        model = FactoryFloor

    id_ = 'conveyor_belt_id'
    feeder = factory.SubFactory(FeederFactory)
    receiver = factory.SubFactory(ReceiverFactory)
    num_slots = 3
    num_pairs = 3
