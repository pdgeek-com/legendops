// Azure Database for PostgreSQL Flexible Server
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: 'legendops-pg'
  location: 'eastus'
  tags: {
    Project: 'LegendOps'
    Environment: 'Dev'
    Owner: 'levioister@pdgeek.com'
    CostCenter: 'MSP-Infrastructure'
  }
  properties: {
    administratorLogin: 'legendops_user'
    administratorLoginPassword: 'JLJCLoPMdcrSOIXL-s8QNQ'
    version: '15'
    storage: { storageSizeGB: 32 }
    network: { publicNetworkAccess: 'Enabled' }
  }
  sku: { name: 'Standard_B1ms', tier: 'Burstable', capacity: 1 }
}
