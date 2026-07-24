# Azure Deployment Plan

> **Status:** Planning

Generated: 2026-07-24T22:15:44Z

---

## 1. Project Overview

**Goal:** Deploy the repository's on-demand Microsoft Fabric demo environment,
create a reusable Fabric workspace, and leave the paid capacity suspended after
setup so it can be resumed only when needed.

**Path:** Add Components to Existing Project

**Deployment scope:** One dedicated Azure resource group containing one Fabric
F2 capacity. Workspace creation and assignment are Fabric data-plane
operations performed after the ARM deployment.

---

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | POC |
| Scale | Small |
| Budget | Cost-Optimized |
| Subscription | `ME-MngEnvMCAP744360-sharmave-1` (`ad92e163-a85e-40cc-bb50-054b0b8197a8`) - confirmed by user |
| Location | `westus3` - confirmed by user |
| Deploying account | `sharmave@MngEnvMCAP744360.onmicrosoft.com` |
| Compliance | No additional data-residency or industry requirements stated |
| Availability | On-demand only; workspace content is unavailable while the capacity is suspended |
| Cost control | Smallest Fabric SKU, automatic post-deploy suspension, explicit `make up` and `make down` lifecycle |

### Cost Estimate and Guardrails

- F2 provides 2 Capacity Units (CUs).
- The current West US 3 retail meter is approximately USD 0.18 per CU-hour,
  giving an estimated active F2 cost of USD 0.36/hour, with a one-minute
  minimum. Continuous operation would be approximately USD 262.80 for 730
  hours before storage, overage, tax, or negotiated pricing.
- The deployment command suspends the capacity after workspace setup. It also
  attempts suspension if a later setup step fails.
- Resuming the capacity resumes billing. Pausing can bill remaining cumulative
  overages and smoothed operations, and persistent OneLake or other storage can
  incur separate charges.
- Fabric capacity overage and Spark autoscale billing are not enabled by this
  deployment.

Pricing references:

- <https://azure.microsoft.com/pricing/details/microsoft-fabric/>
- <https://learn.microsoft.com/fabric/enterprise/pause-resume>
- <https://prices.azure.com/api/retail/prices?$filter=contains(productName,%20%27Fabric%27)%20and%20armRegionName%20eq%20%27westus3%27>

### Policy and Access Findings

- Three subscription policy assignments were found; they are Defender-related
  and do not restrict the selected region, required tags, Fabric resource type,
  or F2 SKU.
- The deploying account inherits `Owner` at management-group scope and has
  `Foundry User` at subscription scope. No new Azure RBAC assignments are
  created.
- The capacity administrator is a tenant-member UPN, as required by Fabric;
  B2B guest administrators are not supported.

---

## 3. Components Detected

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| Fabric infrastructure | Infrastructure as Code | Subscription-scoped Bicep | `infra/main.bicep` |
| Fabric capacity module | Infrastructure as Code | `Microsoft.Fabric/capacities@2023-11-01` | `infra/modules/fabric-capacity.bicep` |
| Capacity lifecycle | Deployment orchestration | Python 3 and Azure CLI | `scripts/fabric/capacity.py` |
| Fabric API client | Data-plane integration | Python 3 and Fabric/Power BI REST APIs | `scripts/fabric/fabric_api.py` |
| Operator commands | Local developer workflow | Make | `Makefile` |

No web application, container, public endpoint, database, virtual network, or
service-to-service secret is part of this deployment.

---

## 4. Recipe Selection

**Selected:** Bicep

**Rationale:**

- The repository already contains a subscription-scoped Bicep deployment and a
  resource-group-scoped capacity module.
- Direct `az deployment sub create` supports the required dedicated resource
  group and provides explicit control over the Fabric ARM resource.
- A typed Python lifecycle CLI performs the required Fabric and Power BI
  data-plane operations that ARM does not cover.
- AZD would add environment and service conventions without improving this
  infrastructure-only workflow.

---

## 5. Architecture

**Stack:** Subscription-scoped Bicep plus Fabric data-plane REST operations

### Service Mapping

| Component | Azure Service | SKU/Configuration |
|-----------|---------------|-------------------|
| Demo boundary | Azure Resource Group | `rg-fabric-github-demo` in `westus3` |
| Fabric compute | Microsoft Fabric capacity | `fcfabricgithubad92e163a85e`, F2/Fabric |
| Demo workspace | Microsoft Fabric workspace | `fabric-with-github-demo`, assigned to the F2 capacity |
| Optional repository connection | Fabric Git integration | Not included in initial deployment; `make fabric-connect` prompts for a PAT later |

### Resource Tags

| Tag | Value |
|-----|-------|
| `environment` | `demo` |
| `workload` | `fabric-with-github` |
| `managed-by` | `bicep` |
| `cost-control` | `suspend-when-idle` |

### Supporting Services Deliberately Omitted

| Service | Reason |
|---------|--------|
| Key Vault | No deployment secret is persisted; an optional GitHub PAT is entered through a hidden prompt and is never written to disk |
| Log Analytics / Application Insights | No hosted application or endpoint is deployed |
| Virtual network / private endpoints | No application ingress or private service-to-service path is required for this POC |
| Azure Automation | The user requested explicit, fast lifecycle commands; automatic suspension already occurs after deployment |

### Deployment Flow

1. Validate Azure CLI, Fabric extension/provider, F2 regional availability, and
   capacity-name availability.
2. Deploy the resource group and Fabric F2 capacity with Bicep.
3. Resolve the capacity's Fabric/Power BI UUID.
4. Create or reuse `fabric-with-github-demo` and assign it to the capacity.
5. Persist only non-secret resource and workspace IDs in
   `.fabric-demo.state.json`.
6. Suspend the capacity and wait for a suspended state.

---

## 6. Provisioning Limit Checklist

### Phase 1: Resource Inventory

| Resource Type | Number to Deploy | Total After Deployment | Limit/Quota | Notes |
|---------------|------------------|------------------------|-------------|-------|
| `Microsoft.Resources/resourceGroups` | 1 | 13 | 980 per subscription | Current count: 12 |
| `Microsoft.Fabric/capacities` (F2) | 1 capacity / 2 CU | 1 capacity / 2 CU | 512 CU in `westus3` | Current usage: 0 CU; 510 CU remain after deployment |
| Microsoft Fabric workspace | 1 | 1 new workspace | Not an Azure ARM provisioning quota | Created through the Fabric REST API |

### Phase 2: Quota and Capacity Evidence

- The Azure Quotas workflow was run first. `Microsoft.Fabric` was not exposed
  through the generic quota provider for this subscription, so the official
  Fabric usage endpoint was used:
  `GET /subscriptions/ad92e163-a85e-40cc-bb50-054b0b8197a8/providers/Microsoft.Fabric/locations/westus3/usages?api-version=2023-11-01`.
- Fabric usage result: `currentValue=0`, `limit=512`, `available=512`.
- Planned F2 consumption: 2 CU; projected usage is 2/512 CU.
- `westus3` is returned in the subscription's F2 SKU eligibility data.
- Existing Fabric capacities in the subscription: 0.
- Capacity name `fcfabricgithubad92e163a85e` is available.
- Existing resource groups: 12; projected resource groups: 13/980.

**Status:** All resources are within limits.

---

## 7. Execution Checklist

### Phase 1: Planning

- [x] Analyze workspace
- [x] Gather requirements
- [x] Confirm subscription and location with user
- [x] Prepare resource inventory
- [x] Fetch quotas and validate capacity using the Azure Quotas workflow
- [x] Scan codebase
- [x] Select recipe
- [x] Plan architecture
- [ ] User approved this paid deployment plan

### Phase 2: Preparation

- [x] Research Fabric capacity and lifecycle requirements
- [x] Generate subscription-scoped Bicep and capacity module
- [x] Generate lifecycle configuration and commands
- [x] Apply secret-safety and cost-suspension controls
- [x] Complete local functional verification
- [ ] Create ignored `scripts/fabric/capacity.local.json` for the confirmed target
- [ ] Update plan status to `Ready for Validation`

### Phase 3: Validation

- [ ] Plan status is `Ready for Validation`
- [ ] Invoke the `azure-validate` skill
- [ ] Bicep build passes
- [ ] Subscription deployment validation passes
- [ ] Subscription deployment what-if matches this inventory
- [ ] Live prerequisite, SKU, name, permission, policy, and quota checks pass
- [ ] Record validation proof below
- [ ] Plan status is `Validated`

### Phase 4: Deployment

- [ ] Invoke the `azure-deploy` skill
- [ ] Create the resource group and F2 capacity
- [ ] Create/reuse and assign the Fabric workspace
- [ ] Verify capacity is suspended after setup
- [ ] Verify local state contains no credential material
- [ ] Update plan status to `Deployed`

---

## 8. Validation Proof

> Pending. The `azure-validate` skill must populate this section with commands,
> results, and timestamps before changing the plan status to `Validated`.

| Check | Command Run | Result | Timestamp |
|-------|-------------|--------|-----------|
| Pending Azure validation | Not run | Pending | Pending |

**Validated by:** Pending

---

## 9. Verification

Deployment is successful only when all of the following are true:

1. Azure reports resource group `rg-fabric-github-demo` in `westus3`.
2. Azure reports F2 capacity `fcfabricgithubad92e163a85e` with successful
   provisioning.
3. Fabric/Power BI resolves the capacity UUID.
4. Fabric reports workspace `fabric-with-github-demo` and its assignment to the
   deployed capacity.
5. Azure reports the final capacity state as suspended/paused.
6. `make status` reports the capacity and recorded workspace.
7. `.fabric-demo.state.json` contains identifiers only, has restrictive local
   permissions, and contains no PAT, token, password, or connection secret.

If automatic suspension fails, the deployment reports a hard error instructing
the operator to run `make down` immediately. Destruction is not part of this
deployment and always requires a separate exact-name confirmation.

---

## 10. Files

| File | Purpose | Status |
|------|---------|--------|
| `.azure/deployment-plan.md` | Deployment source of truth | Complete, awaiting approval |
| `.azure/infrastructure-plan.json` | Approved architecture contract | Complete |
| `infra/main.bicep` | Subscription-scoped resource-group deployment | Complete |
| `infra/modules/fabric-capacity.bicep` | F2 capacity resource | Complete |
| `scripts/fabric/capacity.py` | Deploy/up/down/status/connect/destroy lifecycle | Complete |
| `scripts/fabric/capacity.local.json` | Confirmed ignored deployment configuration | Pending approval |
| `.fabric-demo.state.json` | Non-secret deployed IDs | Created only after successful deployment |

---

## 11. Next Step

> Current: Awaiting explicit approval for the paid F2 deployment.

After approval, preparation will create the ignored local configuration, mark
this plan `Ready for Validation`, invoke `azure-validate`, and only deploy if
all validation checks pass.
