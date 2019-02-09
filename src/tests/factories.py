import factory

from src.domain_models.feeder import Feeder


class FeederFactory(factory.Factory):
    class Meta:
        model = Feeder
    id_ = 'feeder_id'
    components = ['A', 'B']
