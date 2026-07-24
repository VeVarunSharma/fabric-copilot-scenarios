targetScope = 'resourceGroup'

@description('Globally unique lowercase alphanumeric name for the Fabric capacity.')
@minLength(3)
@maxLength(63)
param capacityName string

@description('Azure region for the Fabric capacity.')
param location string

@description('Fabric capacity administrators.')
@minLength(1)
param adminMembers array

@description('Tags applied to the Fabric capacity.')
param tags object

resource capacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: capacityName
  location: location
  tags: tags
  sku: {
    name: 'F2'
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: adminMembers
    }
  }
}

output capacityName string = capacity.name
output capacityResourceId string = capacity.id
