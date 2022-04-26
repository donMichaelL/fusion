import json, time
from redis_connection import RedisConnection
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro
import avro.schema

value_schema = avro.schema.Parse(open("./schemas/FusionAlert.avsc","rb").read())
avro_producer = AvroProducer({
    'bootstrap.servers': "88.28.218.13:9097",
    'schema.registry.url': "http://88.28.218.13:8081"},
    default_value_schema=value_schema)


def publish_to_kafka(mission_id, vehicle_id, position, alert_level):
    example_time = int(round(time.time() * 1000))
    message = {
        "alert_id": 3000,
        "alert_start_time": example_time,
        "alert_end_time": example_time + 5,
        "alert_text": "Detected object of unidentified boat was not matched with any of the available AIS tracks. Further investigation about its identity is needed.",
        "alert_title": "Fusion Alert",
        "timestamp": example_time,
        "mission_id": mission_id,
        "tracked_entity_id": int(vehicle_id),
        "alert_level": alert_level,
        "alert_status": "ALERT_ACTIVE",
        "location": {
            "type": "Point",
            "coordinates": [{
                "latitude": position[0],
                "longitude": position[1]
            }],
            "radius": 1.0
        },
    }
    print('Alert was sent to Kafka!')
    avro_producer.produce(topic="FusionAlert", value=message)


class LidarMsg:
    def __init__(self, vehicle_id, position, data, timestamp):
        self._redis_client = RedisConnection.client
        self.vehicle_id = vehicle_id
        self.position = position
        self.yaw = 0
        self.data = data
        self.timestamp = timestamp

    def calculate_distance(self):
        for obj in self.data:
            result = (obj['x']**2 + obj['y']**2)**(1/2)
            if result <= 50:
                self.report_value(result)

    def report_value(self, distance):
        status = self._redis_client.get(self.vehicle_id)
        if (status != None) and ('confidence' in json.loads(status)) and (abs(self.timestamp-json.loads(status)['timestamp']) <=10):
            pass
            # publish_to_kafka(self.vehicle_id, self.position)
        else:
            self._redis_client.set(self.vehicle_id, json.dumps({
                'timestamp': self.timestamp,
                'distance': distance,
            }))

    @staticmethod
    def is_eligible(yaw):
        return yaw == 0 if True else False



class RiskMsg:
    def __init__(self, mission_id, vehicle_id, alert_level):
        self._redis_client = RedisConnection.client
        self.mission_id = mission_id
        self.vehicle_id = vehicle_id
        self.alert_level = alert_level
        self.position = [1.069115391259969, 0.5044335441871729]

    def calculate_distance(self):
        print('Processing')
        print(self.mission_id)
        status = self._redis_client.get(self.mission_id)
        if (status == None):
            publish_to_kafka(self.mission_id, self.vehicle_id, self.position, self.alert_level)
            self._redis_client.set(self.mission_id, json.dumps({
                'status': 'OK',
            }))


class VisualMsg:
    def __init__(self, mission_id, vehicle_id, sequence):
        self._redis_client = RedisConnection.client
        self.mission_id = mission_id
        self.vehicle_id = vehicle_id
        self.position = None
        self.sequence = sequence
        self.timestamp = 0
        self.confidence = 0

    def calculate_confidence(self):
        print('Processing')
        for seq in self.sequence:
            for loc in seq['localization']:
                if loc['class'] in ['boat', 'ship', 'inflated', 'speedboat']  and loc['confidence'] >= 0.6:
                    print('We have confidence')
                    self.timestamp = seq['timestamp']
                    self.confidence = loc['confidence']
                    self.position = (
                        loc['latitude'],
                        loc['longitude']
                    )
                    self.report_value()
                    return;

    def get_alert_level(self):
        if self.confidence > 0.9:
            return 'HIGH'
        elif self.confidence > 0.80:
            return 'MEDIUM'
        else:
            return 'LOW'

    def report_value(self):
        # status = self._redis_client.get(self.vehicle_id)
        publish_to_kafka(self.mission_id, self.vehicle_id, self.position, self.get_alert_level())
        # if (status != None) and ('distance' in json.loads(status)) and (abs(self.timestamp-json.loads(status)['timestamp']) <=10):
        #     publish_to_kafka(self.vehicle_id, self.position)
        # else:
        #     self._redis_client.set(self.vehicle_id, json.dumps({
        #         'timestamp': self.timestamp,
        #         'confidence': self.confidence,
        #     }))
