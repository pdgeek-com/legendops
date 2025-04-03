
param tags object = {
  Project: 'LegendOps'
  Environment: 'Dev'
  Owner: 'levi@pdgeek.com'
  CostCenter: 'MSP-Infrastructure'
}

param RESOURCE_GROUP: string
param LOCATION: string
param POSTGRES_USER: string
param POSTGRES_PASSWORD: string
param POSTGRES_DB: string
param KEYVAULT_NAME: string
param STORAGE_ACCOUNT: string
param LOG_ANALYTICS_WORKSPACE: string
param AZURE_CLIENT_ID: string
param AZURE_TENANT_ID: string
module web './web.bicep' = { name: 'web_module' }
module auth './auth.bicep' = { name: 'auth_module' }
module billing './billing.bicep' = { name: 'billing_module' }
module catalog './catalog.bicep' = { name: 'catalog_module' }
module frontend './frontend.bicep' = { name: 'frontend_module' }
module postgres './postgres.bicep' = { name: 'postgres_module' }