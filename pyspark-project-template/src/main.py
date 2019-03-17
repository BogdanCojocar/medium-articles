import argparse
import os
from pyspark.sql import SparkSession
import importlib
import sys
import json

if os.path.exists('jobs.zip'):
    sys.path.insert(0, 'jobs.zip')


def get_config(path, job):
    file_path = path + '/' + job + '/resources/args.json'
    with open(file_path, encoding='utf-8') as json_file:
        config = json.loads(json_file.read())
    config['relative_path'] = path
    return config


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='My pyspark job arguments')
    parser.add_argument('--job', type=str, required=True, dest='job_name',
                        help='The name of the spark job you want to run')
    parser.add_argument('--res-path', type=str, required=True, dest='res_path',
                        help='Path to the jobs resurces')

    args = parser.parse_args()

    spark = SparkSession\
        .builder\
        .appName(args.job_name)\
        .getOrCreate()

    job_module = importlib.import_module('jobs.%s' % args.job_name)
    res = job_module.run(spark, get_config(args.res_path, args.job_name))

    print('[JOB {job} RESULT]: {result}'.format(job=args.job_name, result=res))
