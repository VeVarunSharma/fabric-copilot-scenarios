# Scenario 03 - IoT PySpark notebook generation

This scenario shows how GitHub Copilot can draft an operationally useful Fabric PySpark notebook for telemetry processing while the engineer reviews data contracts and run-time safeguards.

- [Sample prompt](sample-prompt.md)
- [Expected output](expected-output.md)
- [Extension exercises](extension-exercises.md)

## Business problem
An operations team receives high-volume IoT telemetry and needs a repeatable notebook that lands raw data, removes duplicates, rejects out-of-range measurements, computes rolling device metrics, and writes curated Delta outputs.

## Target personas and prerequisites
**Primary personas**
- Fabric data engineers authoring PySpark notebooks
- Manufacturing or operations analysts reviewing telemetry rules
- Platform owners validating Delta output conventions and logging

**Prerequisites**
- Working knowledge of Spark DataFrames and window functions
- Familiarity with Delta Lake write patterns
- Ability to review schema definitions and data-quality logic

## Manual baseline
Without Copilot, a practitioner usually:
1. Creates notebook cells and imports from scratch.
2. Manually types the telemetry `StructType` and column-level range checks.
3. Builds deduplication logic with window functions.
4. Adds operational logging and validation cells after the transformation logic is already written.
5. Repeats the same write and validation patterns for curated and quarantine outputs.

The manual work is not conceptually hard, but it is repetitive and easy to miss in one or two cells.

## Copilot-assisted workflow
1. Provide the notebook target path, dataset path, and the required telemetry columns.
2. Ask Copilot to generate a Fabric-compatible notebook outline with explicit schema, deduplication, range checks, windowed metrics, Delta writes, logging, and validation.
3. Refine the prompt until the notebook reflects the team's expected table names, parameter cell, and quality thresholds.
4. Review the generated notebook carefully before any workspace import or scheduled run.

## Sample Fabric artifact
The planned canonical notebook is [../../notebooks/iot-telemetry/telemetry_processing.ipynb](../../notebooks/iot-telemetry/telemetry_processing.ipynb).

The planned dataset path is [../../datasets/synthetic/iot-telemetry/](../../datasets/synthetic/iot-telemetry/).

A strong notebook draft should include:
- An explicit parameter cell for `process_date`, output locations, and table names
- A `StructType` for the telemetry contract rather than schema inference
- Deduplication by device and event time using window logic
- Range checks and quarantine output for invalid measurements
- Rolling or tumbling metrics for device health analysis
- Delta writes, structured logging, and validation cells

## Validation
After Copilot drafts the notebook, verify that:
- The schema matches the expected telemetry columns and data types.
- Deduplication keeps the latest valid record per device and event timestamp.
- Range checks move invalid rows to quarantine instead of silently dropping them.
- Window calculations use the intended partition keys and time order.
- Delta writes do not rely on hardcoded workspace or lakehouse identifiers.

## Learning objectives
- Turn a notebook requirement into a precise prompt that produces runnable scaffolding.
- Review generated Spark code for data-contract correctness instead of typing boilerplate.
- Distinguish between logic that Copilot can draft quickly and logic that still needs domain review.
- Use validation cells as part of the generation request, not as an afterthought.

## What work did Copilot eliminate?
Copilot eliminates the repetitive notebook scaffold: imports, schema declarations, deduplication windows, logging setup, Delta write blocks, and the first draft of validation cells. The engineer can spend time on rule accuracy, operational fit, and data-contract review.

## Responsible use/security
- Keep all examples synthetic and free of device identifiers that map to real customers or facilities.
- Do not hardcode workspace IDs, storage locations, or credentials in generated notebook code.
- Review logging so operational messages do not expose sensitive payload contents.
- Validate quarantine handling before the notebook is scheduled in production.
