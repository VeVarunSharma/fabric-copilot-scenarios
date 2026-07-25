targetScope = 'subscription'

@description('Azure region for the resource group and Fabric capacity.')
param location string = deployment().location

@description('Dedicated resource group for the disposable Fabric demo.')
param resourceGroupName string = 'rg-fabric-github-demo'

@description('Fabric capacity administrators. Administrators must be members of the Fabric tenant and cannot be B2B guests.')
@minLength(1)
param adminMembers array

@description('Globally unique lowercase alphanumeric name for the Fabric capacity.')
@minLength(3)
@maxLength(63)
param capacityName string = 'fcfabricgithub${substring(replace(subscription().subscriptionId, '-', ''), 0, 12)}'

@description('Tags applied to all Azure resources in the demo.')
param tags object = {
  environment: 'demo'
  workload: 'fabric-with-github'
  'managed-by': 'bicep'
  'cost-control': 'suspend-when-idle'
}

resource demoResourceGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module fabricCapacity './modules/fabric-capacity.bicep' = {
  name: 'fabricCapacity'
  scope: demoResourceGroup
  params: {
    adminMembers: adminMembers
    capacityName: capacityName
    location: location
    tags: tags
  }
}

output capacityName string = fabricCapacity.outputs.capacityName
output capacityResourceId string = fabricCapacity.outputs.capacityResourceId
output resourceGroupName string = demoResourceGroup.name
