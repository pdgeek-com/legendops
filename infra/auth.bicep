// auth Bicep module
resource auth 'Microsoft.Web/containerApps@2022-03-01' = {
  name: 'auth-app'
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
        name: 'auth'
        image: 'ghcr.io/pdgeek-com/legendops/auth:dev-latest'
      }]
    }
  }
}
