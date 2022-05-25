from typing import Container
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Token
from imports.azurerm import *

class StackVariables:
    stack_name = "cdktfsentml"
    location = "UK South"
    rg_name = f"{stack_name}-rg"
    storage_name = f"{stack_name}storage"
    sc_name = f"{stack_name}container"
    ap_name = f"{stack_name}insights"
    sp_name = f"{stack_name}-service-plan"
    function_name = f"{stack_name}-function"
    vn_conn_function_name = f"{stack_name}-vn-conn"
    cog_name = f"{stack_name}-ml-cognitive"
    # TODO: add the values here before deployment
    azure_language_endpoint = ""
    azure_language_key = ""

    tag = {
        "ENV": "Prod",
        "PROJECT": "ML_Pipeline"
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

        storage_acount = StorageAccount(self, vars.storage_name,
            name = vars.storage_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            account_tier = "Standard",
            account_kind = "Storage",
            account_replication_type = "LRS"
        )

        containers = ["azure-webjobs-hosts", "azure-webjobs-secrets", "scm-releases"]
        for container in containers:
            StorageContainer(self, container,
                name = container,
                storage_account_name  = storage_acount.name,
                container_access_type = "private"
            )

        app_insights = ApplicationInsights(self, vars.ap_name,
            name = vars.ap_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            application_type    = "web"
        )

        service_plan = AppServicePlan(self, vars.sp_name,
            name = vars.sp_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            kind = "FunctionApp",
            reserved = True,
            sku = {
                "tier": "Dynamic",
                "size": "Y1"
            }
        )

        FunctionApp(self, vars.function_name,
            name = vars.function_name,
            location = vars.location,
            resource_group_name = Token().as_string(resource_group.name),
            app_service_plan_id = service_plan.id,
            storage_account_name = Token().as_string(storage_acount.name),
            storage_account_access_key = storage_acount.primary_access_key,
            https_only = True,
            version = "~4",
            os_type = "linux",
            app_settings = {
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "APPINSIGHTS_INSTRUMENTATIONKEY": f"{app_insights.instrumentation_key}",
                "AzureWebJobsStorage": storage_acount.primary_access_key,
                "AZURE_LANGUAGE_ENDPOINT": vars.azure_language_endpoint,
                "AZURE_LANGUAGE_KEY": vars.azure_language_key
            },
            site_config = {
                "linux_fx_version": "Python|3.8",      
                "ftps_state": "Disabled"
            }
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
        
        TerraformOutput(self, 'cognitive_endpoint',
            value = cog_account.endpoint
        )


app = App()
MLAzureStack(app, vars.stack_name)

app.synth()
