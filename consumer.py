
from confluent_kafka import KafkaError
from confluent_kafka.avro.serializer import SerializerError
from random import random

from settings import BOOTSTRAP_SERVER, SCHEMA_REGISTRY
from models import LidarMsg, VisualMsg, RiskMsg
from utils import StringKeyAvroConsumer



c = StringKeyAvroConsumer({
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': str(random()),
    'schema.registry.url': SCHEMA_REGISTRY
})

c.subscribe(['VisualDetections', 'WaterVehicles', 'RiskAlert'])


while True:
    try:
        print('Running....')
        msg = c.poll(10)
    except SerializerError as e:
        print("Message deserialization failed for: {}".format(e))
        break
    if msg is None:
        print('No Message')
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            continue
        else:
            print(msg.error())
            break


    if msg.topic() == 'VisualDetections':
        v = VisualMsg(
            msg.value()['mission_id'],
            msg.value()['vehicle_id'],
            msg.value()['sequence']
        )
        v.calculate_confidence()

    elif msg.topic() == 'WaterVehicles':
        print("Received WaterVehicles msg: ", msg, msg.value()['name_vehicle'])
    else:
        pass
        print('A new message was received')
        # w = RiskMsg(
        #     msg.value()['mission_id'],
        #     msg.value()['tracked_entity_id'],
        #     msg.value()['alert_level'],
        # )
        # w.calculate_distance()

c.close()
