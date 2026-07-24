# Live-demo checklist

## Before the customer session

- [ ] Use a Windows machine with a current Power BI Desktop build.
- [ ] Enable the Power BI project and TMDL preview features required by the local environment.
- [ ] Confirm the Power BI Modeling MCP server is registered and responsive.
- [ ] Confirm the Power BI Report Authoring skill is available.
- [ ] Confirm Desktop Bridge can open or reload a local PBIP and capture screenshots.
- [ ] Install the certified HTML Content (lite) visual from AppSource if the showcase card is in scope.
- [ ] Clone the repository to a short local path without changing source-controlled files.
- [ ] Create or identify a disposable PBIP working folder for the live authoring sequence.
- [ ] Confirm no customer data, tenant IDs, secrets, PHI, PII, or confidential material is present.
- [ ] Run the focused automated tests.

## Live path

1. Show the public source manifest and the exact Statistics Canada attribution.
2. Explain that the table is archived and historical and that 2022 is a comparability break.
3. Set `CCHS Data Root` to the clean-clone snapshot folder through Modeling MCP.
4. Build or inspect the eight tables, seven relationships, and explicit measures.
5. Refresh and execute each DAX validation block independently.
6. Ask the Report Authoring skill to apply the committed three-page brief.
7. Run report validation.
8. Use Desktop Bridge to open or reload the PBIP.
9. Capture `BC Overview`, `Trend and Demographics`, and `Data Quality and Methodology`.
10. Compare the live result with the committed completed project.

## Visual acceptance

- [ ] Page order is correct.
- [ ] Default state is Perceived Health, 2022, total age 12 years and over, both sexes, and percent estimate.
- [ ] BC shows 51.3%, Canada excluding territories shows 55.3%, and the difference is -4.0 percentage points.
- [ ] The HTML spotlight renders, or the dependency is called out without blocking the native fallback.
- [ ] The province chart shows provinces only.
- [ ] The trend page visibly warns about the 2022 redesign.
- [ ] Age and sex visuals are populated.
- [ ] E is labelled use with caution.
- [ ] F and x estimates remain blank.
- [ ] Exact source attribution is visible.
- [ ] No visual is broken, empty at the default state, clipped, or overlapping.

## Fallback path

If Modeling MCP, report authoring, Desktop Bridge, or the custom visual is unavailable:

1. Stop the failing live-authoring step rather than improvising unsupported behavior.
2. Open the committed `semantic-models/CCHSHealth/CCHSHealth.pbip`.
3. Use the committed DAX queries and automated test results as model evidence.
4. Use the native fallback card if HTML Content (lite) is unavailable.
5. Use approved screenshots from the last successful Windows acceptance pass.
6. State which dependency was unavailable and which parts were still verified.

## After the session

- [ ] Remove temporary customer-specific paths from the working copy.
- [ ] Confirm no PBIX cache, credentials, screenshots with identifiers, or third-party visual binaries were added to Git.
- [ ] Record open decisions about the future customer extract.
- [ ] Keep source approval, privacy classification, methodology interpretation, and release acceptance assigned to named human owners.
