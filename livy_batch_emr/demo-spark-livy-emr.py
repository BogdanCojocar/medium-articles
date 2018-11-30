import json, logging, requests
import time

def run_spark_job(master_dns):
    response = spark_submit(master_dns)
    track_statement_progress(master_dns, response)

def spark_submit(master_dns):

    host = 'http://' + master_dns + ':8999'
    data = {'className': "com.app.RunBatchJob", "conf":{"spark.hadoop.fs.s3a.impl":"org.apache.hadoop.fs.s3a.S3AFileSystem"}, 'file': "s3a://your_bucket/spark_batch_job-1.0-SNAPSHOT-shadow.jar"}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(host + '/batches', data=json.dumps(data), headers=headers)

    logging.info(response.json())
    return response.headers

def track_statement_progress(master_dns, response_headers):
    statement_status = ''
    host = 'http://' + master_dns + ':8999'
    session_url = host + response_headers['location'].split('/statements', 1)[0]

    while statement_status != 'success':
        statement_url = host + response_headers['location']
        statement_response = requests.get(statement_url, headers={'Content-Type': 'application/json'})
        statement_status = statement_response.json()['state']
        logging.info('Statement status: ' + statement_status)

        lines = requests.get(session_url + '/log', headers={'Content-Type': 'application/json'}).json()['log']
        for line in lines:
            logging.info(line)

        if statement_status == 'dead':
            raise ValueError('Exception in the app caused it to be dead: ' + statement_status)

        if 'progress' in statement_response.json():
            logging.info('Progress: ' + str(statement_response.json()['progress']))
        time.sleep(10)

if __name__ == '__main__':
    master_dns = "YOUR_CLUSTER_DNS"
    run_spark_job(master_dns)
