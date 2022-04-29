import argparse
import logging
import sys
from river import datasets
import requests
import json
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FileSink, OutputFileConfig
from pyflink.common.serialization import Encoder

def run_consumer(output_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    # write all the data to one file
    env.set_parallelism(1)

    # get the credit card data
    dataset = datasets.CreditCard()

    # create a small collection of items
    i = 0
    num_of_items = 2000
    items = []
    for x, y in dataset:
        if i == num_of_items:
            break
        i+=1
        items.append((json.dumps(x), y))

    credit_stream = env.from_collection(
        collection=items,
        type_info=Types.ROW([Types.STRING(), Types.STRING()]))

    # detect fraud in transactions
    fraud_data = credit_stream.map(lambda data: \
        json.dumps(requests.post('http://localhost:9000/predict', \
                        json={'x': data[0], 'y': data[1]}).json()), \
                        output_type=Types.STRING())

    # save the results to a file
    fraud_data.sink_to(
        sink=FileSink.for_row_format(
            base_path=output_path,
            encoder=Encoder.simple_string_encoder())
        .build()
    )

    # submit for execution
    env.execute()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output',
        dest='output',
        required=True,
        help='Output file to write fraud results to')

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    run_consumer(known_args.output)
