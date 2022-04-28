import os

BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER', "192.168.40.10:9095")
SCHEMA_REGISTRY = os.getenv('SCHEMA_REGISTRY', "http://192.168.40.10:8081")


# avro_producer = AvroProducer({
#     'bootstrap.servers': "192.168.40.10:9095",
#     'schema.registry.url': "http://192.168.40.10:8081"},
#     default_value_schema=value_schema)

# avro_producer = AvroProducer({
#     'bootstrap.servers': "88.28.218.13:9097",
#     'schema.registry.url': "http://88.28.218.13:8081"},
#     default_value_schema=value_schema)
