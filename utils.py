import json
import types

from confluent_kafka.avro import AvroConsumer


class MappingProxyEncoder(json.JSONEncoder):
    # This is a hack to get around a bug in confluent-kafka
    # https://github.com/confluentinc/confluent-kafka-python/issues/610
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._base_default = json.JSONEncoder.default
    def __enter__(self):
        """Replaces JSONEncoder.default with a new function that can handle MappingProxyType"""
        base_default = self._base_default
        def default(s, obj):
            if isinstance(obj, types.MappingProxyType):
                return obj.copy()
            else:
                return base_default(s, obj)
        json.JSONEncoder.default = default  # type: ignore
    def __exit__(self, exc_type, exc_val: Exception, exc_tb) -> bool:
        """Returns JSONEncoder.default to its original state"""
        json.JSONEncoder.default = self._base_default  # type: ignore
        return True


class StringKeyAvroConsumer(AvroConsumer):
    def __init__(self, config):
        super(StringKeyAvroConsumer, self).__init__(config)

    def poll(self, timeout=None):
        """
        This is an overriden method from AvroConsumer class. This handles message
        deserialization using avro schema for the value only.

        @:param timeout
        @:return message object with deserialized key and value as dict objects
        """
        if timeout is None:
            timeout = -1
        message = super(AvroConsumer, self).poll(timeout)
        if message is None:
            return None
        if not message.value() and not message.key():
            return message
        if not message.error():
            if message.value() is not None:
                decoded_value = self._serializer.decode_message(message.value())
                message.set_value(decoded_value)
            # Don't try to decode the key
        return message
