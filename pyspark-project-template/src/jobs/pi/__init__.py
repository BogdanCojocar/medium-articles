from random import random
from operator import add


NUMBER_OF_STEPS_FACTOR = 100000


def f(_):
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0


def run(spark, config):
    number_of_steps = config['partitions'] * NUMBER_OF_STEPS_FACTOR
    count = spark.sparkContext\
        .parallelize(range(1, number_of_steps + 1),
                     config['partitions']).map(f).reduce(add)
    return 4.0 * count / number_of_steps
