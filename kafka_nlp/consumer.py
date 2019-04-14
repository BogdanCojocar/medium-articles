from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
import uuid
import argparse
import spacy

nlp = spacy.load('en')

def nlp_processing(message):
    doc = nlp(message['data'])
    print('word', 'lemma', 'part-of-speech', 'is-alpha', 'is-stop')
    for word in doc:
        print(word.text, word.lemma_, word.pos_, word.is_alpha, word.is_stop)

    print('word', 'entity')
    for word in doc.ents:
        print(word.text, word.label_)
    print()


def confluent_kafka_consumer(args):

    msg_consumed_count = 0
    conf = {'bootstrap.servers': args.bootstrap_servers,
            'group.id': uuid.uuid1(),
            'session.timeout.ms': 6000,
            'default.topic.config': {
                'auto.offset.reset': 'latest'
            },
            'schema.registry.url': args.schema_registry
    }

    consumer = AvroConsumer(conf)
    consumer.subscribe([args.topic])

    while True:

        try:
            msg = consumer.poll(1)
            if msg:
                msg_consumed_count += 1
                nlp_processing(msg.value())
        except SerializerError as e:
            print('Message deserialization failed for {}: {}'.format(msg, e))
            break

        if msg is None:
            continue

        if msg.error():
            print("AvroConsumer error: {}".format(msg.error()))
            continue

        if msg_consumed_count >= int(args.msg_count):
            break

    consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluent Kafka avro cosumer")

    parser.add_argument('-b', dest="bootstrap_servers",
                            default="127.0.0.1:9092", help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry",
                            default="http://127.0.0.1:9999", help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="test",
                            help="Topic name")
    parser.add_argument('-m', dest="msg_count", default='5', help="Number of messages")

    args = parser.parse_args()
    confluent_kafka_consumer(args)
