from typing import Container
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Token
from imports.azurerm import *

class StackVariables:
    stack_name = "aksseldonml"
    location = "UK South"
    rg_name = f"{stack_name}-rg"
    k8s_cluster_name = f"{stack_name}-aks"
    container_reg_name = f"seldonservice"
    cog_name = f"{stack_name}-ds-ml-cognitive"
    key_vault_name = f"{stack_name}-vault"
    secret_endpoint = "cognitiveendpoint"
    secret_key = "cognitivekey"

    tag = {
        "ENV": "Prod",
        "PROJECT": "ML_AKS_Pipeline"
    }

vars = StackVariables()

class MLAzureStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AzurermProvider(self, "Azurerm",
            features = {}
        )

        resource_group = ResourceGroup(self, vars.rg_name,
            name = vars.rg_name,
            location = vars.location,
            tags = vars.tag
        )

        aks_cluster = KubernetesCluster(self, vars.k8s_cluster_name,
            name = vars.k8s_cluster_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            dns_prefix = vars.stack_name,
            default_node_pool = {
                "name": "default",
                "node_count": 2,
                "vm_size": "standard_d2_v4"
            },
            identity = {
                "type": "SystemAssigned"
            },
            tags = vars.tag
        )

        cog_account = CognitiveAccount(self, vars.cog_name,
            name = vars.cog_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            kind = "TextAnalytics",
            sku_name = "F0",
            custom_subdomain_name = vars.cog_name,
            public_network_access_enabled = True,
            tags = vars.tag
        )

        container = ContainerRegistry(self, vars.container_reg_name,
            name = vars.container_reg_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            sku = "Basic"
        )

        client_config = DataAzurermClientConfig(self, "current")

        
        key_vault = KeyVault(self, vars.key_vault_name,
            name = vars.key_vault_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            tenant_id = client_config.tenant_id,
            sku_name = "premium",

            access_policy = [KeyVaultAccessPolicy(
                tenant_id = client_config.tenant_id,
                object_id = client_config.object_id,
                key_permissions = [
                    "Create",
                    "Get",
                ],
                secret_permissions = [
                    "Set",
                    "Get",
                    "Delete",
                    "Purge",
                    "Recover"
                ]
            )]
        )

        cognitive_endpoint_secret = KeyVaultSecret(self, vars.secret_endpoint,
            name = vars.secret_endpoint,
            value = cog_account.endpoint,
            key_vault_id = key_vault.id
        )

        cognitive_key_secret = KeyVaultSecret(self, vars.secret_key,
            name = vars.secret_key,
            value = cog_account.primary_access_key,
            key_vault_id = key_vault.id
        )
        
        TerraformOutput(self, 'resource_group',
            value = resource_group.id
        )
        TerraformOutput(self, 'container_id',
            value = container.id,
        )
        TerraformOutput(self, 'container_url',
            value = container.login_server,
        )
        TerraformOutput(self, 'cognitive_endpoint_secret_id',
            value = cognitive_endpoint_secret.id
        )
        TerraformOutput(self, 'cognitive_key_secret_id',
            value = cognitive_key_secret.id
        )


app = App()
MLAzureStack(app, vars.stack_name)

app.synth()
