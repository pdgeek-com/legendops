// web Bicep module
resource web 'Microsoft.Web/containerApps@2022-03-01' = {
  name: 'web-app'
  location: 'eastus'
  tags: {
    Project: 'LegendOps'
    Environment: 'Dev'
    Owner: 'levioister@pdgeek.com'
    CostCenter: 'MSP-Infrastructure'
  }
  properties: {
    kubeEnvironmentId: '' // Provide environment
    configuration: {
      ingress: { external: true, targetPort: 5000 }
    }
    template: {
      containers: [{
        name: 'web'
        image: 'ghcr.io/pdgeek-com/legendops/web:dev-latest'
      }]
    }
  }
}
