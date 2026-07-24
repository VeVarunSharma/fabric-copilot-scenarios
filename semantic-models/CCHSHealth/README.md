# CCHSHealth Power BI project

This portable Power BI Project uses the normalized aggregate public-data contract in `datasets/public/cchs-annual/snapshot/`. It demonstrates a historical 2015-2022 Canadian Community Health Survey model for British Columbia comparisons.

The committed `CCHS Data Root` parameter is repository-relative so no developer-specific path is stored in source control. Before refresh, set it to the absolute local snapshot folder with the Power BI Modeling MCP server or Power Query parameters. On Windows, open `CCHSHealth.pbip`, refresh the model, and run `validation/model-validation.dax`.

The semantic model is authored in TMDL as the source-controlled fallback because the Modeling MCP server is unavailable in the macOS development environment. The customer demonstration uses Modeling MCP to set the local parameter, apply or inspect the model, refresh, and execute the validation queries.

Source: Statistics Canada table 13-10-0096-01, *Health characteristics, annual estimates, inactive*. This is an adapted historical demonstration and does not constitute an endorsement by Statistics Canada or the Government of British Columbia.
