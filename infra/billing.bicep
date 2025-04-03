// billing Bicep module
resource billing 'Microsoft.Web/containerApps@2022-03-01' = {
  name: 'billing-app'
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
        name: 'billing'
        image: 'ghcr.io/pdgeek-com/legendops/billing:dev-latest'
      }]
    }
  }
}
