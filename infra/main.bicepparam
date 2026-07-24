using './main.bicep'

param location = 'westus3'
param resourceGroupName = 'rg-fabric-github-demo'

// Replace this value before deploying the parameter file directly.
param adminMembers = [
  'replace-with-your-upn@example.com'
]
