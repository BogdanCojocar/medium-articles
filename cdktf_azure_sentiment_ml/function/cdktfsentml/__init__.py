import logging
import os

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    sentence = req.params.get('sentence')
    if not sentence:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            sentence = req_body.get('sentence')

    if sentence:
        result = text_analytics_client.analyze_sentiment([sentence])
        return func.HttpResponse(f"Sentiment of latest request is: {result[0].sentiment}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function did not execute sucessfully. Please pass a sentence in the request to get a valid response.",
             status_code=404
        )
