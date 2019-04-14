import confluent_kafka
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import argparse
import uuid
import random

value_schema_str = """
{
   "namespace": "my.schema",
   "name": "value",
   "type": "record",
   "fields" : [
     {
       "name" : "data",
       "type" : "string"
     }
   ]
}
"""

key_schema_str = """
{
   "namespace": "my.schema",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "key",
       "type" : "string"
     }
   ]
}
"""

simple_messages = [
'I love this pony',
'This restaurant is great',
'The weather is bad today',
'I will go to the beach this weekend',
'She likes to swim',
'Apple is a great company'
]

def confluent_kafka_producer_performance(args):

    value_schema = avro.loads(value_schema_str)
    key_schema = avro.loads(key_schema_str)

    avroProducer = AvroProducer({
        'bootstrap.servers': args.bootstrap_servers,
        'schema.registry.url': args.schema_registry
    },
    default_key_schema=key_schema,
    default_value_schema=value_schema)

    messages_to_retry = 0

    for i in range(int(args.msg_count)):
        value = {"data": random.choice(simple_messages)}
        key = {"key": str(uuid.uuid4())}
        try:
            avroProducer.produce(topic=args.topic, value=value, key=key)
        except BufferError as e:
            messages_to_retry += 1

    for i in range(messages_to_retry):
        avroProducer.poll(0)
        try:
            avroProducer.produce(topic=args.topic, value=value, key=key)
        except BufferError as e:
            avroProducer.poll(0)
            avroProducer.produce(topic=args.topic, value=value, key=key)

    avroProducer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluent Kafka avro producer")

    parser.add_argument('-b', dest="bootstrap_servers",
                        default="127.0.0.1:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                        default="http://127.0.0.1:9999", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="test",
                        help="Topic name")
    parser.add_argument('-m', dest="msg_count", default='5', help="Number of messages")

    args = parser.parse_args()
    confluent_kafka_producer_performance(args)

    print('we\'ve sent {count} messages to {brokers}'.format(count=args.msg_count, brokers=args.bootstrap_servers))
