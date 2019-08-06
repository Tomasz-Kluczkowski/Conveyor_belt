# from src.domain_models.factory_floor import FactoryFloor
# from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
#
#
# class TestFactoryFloor:
#     def test_run_factory_one_product_created(self, factory_floor_factory, feeder_factory):
#         config = FactoryFloorConfig
#         config.NUM_STEPS = 11
#         feeder = feeder_factory(
#             feed_input=['A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
#         )
#         factory_floor: FactoryFloor = factory_floor_factory(
#             config=config,
#             feeder=feeder
#         )
#         factory_floor.run()
#         assert factory_floor.receiver.received_items == ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P']
#
#     def test_run_factory_two_products_created(self, factory_floor_factory, feeder_factory):
#         config = FactoryFloorConfig
#         config.NUM_STEPS = 13
#         feeder = feeder_factory(
#             feed_input=['A', 'B', 'A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
#         )
#         factory_floor: FactoryFloor = factory_floor_factory(
#             config=config,
#             feeder=feeder
#         )
#         factory_floor.run()
#         assert factory_floor.receiver.received_items == [
#             'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P', 'E', 'P'
#         ]
#
#     def test_run_factory_three_products_created(self, factory_floor_factory, feeder_factory):
#         config = FactoryFloorConfig
#         config.NUM_STEPS = 15
#         feeder = feeder_factory(
#             feed_input=['A', 'B', 'A', 'B', 'A', 'B', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E']
#         )
#         factory_floor: FactoryFloor = factory_floor_factory(
#             config=config,
#             feeder=feeder
#         )
#         factory_floor.run()
#         assert factory_floor.receiver.received_items == [
#             'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'P', 'E', 'P', 'E', 'P'
#         ]
