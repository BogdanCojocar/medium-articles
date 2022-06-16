from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import json

class health_entity:
    def __init__(self):
        credential = DefaultAzureCredential()
        vault_url = 'https://aksseldonml-vault.vault.azure.net/'
        client = SecretClient(vault_url=vault_url, credential=credential)

        # get credentials
        cognitive_endpoint = client.get_secret('cognitiveendpoint').value
        cognitive_key = client.get_secret('cognitivekey').value
        
        ta_credential = AzureKeyCredential(cognitive_key)
        text_analytics_client = TextAnalyticsClient(
            endpoint = cognitive_endpoint, 
            credential = ta_credential)

        self.client = text_analytics_client

    def predict(self, data, meta=[]):

        poller = self.client.begin_analyze_healthcare_entities(data)
        result = poller.result()

        # create a model result with entities and different roles
        model_result = []
        for _, doc in enumerate(result):
            for entity in doc.entities:
                model_result.append({
                    'entity': {
                        'name': entity.text,
                        'category': entity.category,
                        'confidence_score': entity.confidence_score
                    }
                })
            for relation in doc.entity_relations:
                relation_roles = {'relation_type': '', 'roles': []}
                relation_roles['relation_type'] = relation.relation_type
                for role in relation.roles:
                    relation_roles['roles'].append({'role': role.name, 'entity': role.entity.text})
                model_result.append(relation_roles)

        print(model_result)

        return json.dumps(model_result)
    
        

    

    