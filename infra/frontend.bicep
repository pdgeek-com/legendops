// Frontend deployment as Azure Static Web App
resource frontend 'Microsoft.Web/staticSites@2022-03-01' = {
  name: 'legendops-frontend'
  location: 'eastus'
  sku: { name: 'Free' }
  tags: {
    Project: 'LegendOps'
    Environment: 'Dev'
    Owner: 'levioister@pdgeek.com'
    CostCenter: 'MSP-Infrastructure'
  }
  properties: {
    repositoryUrl: 'https://github.com/pdgeek-com/legendops'
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'build'
    }
  }
}
