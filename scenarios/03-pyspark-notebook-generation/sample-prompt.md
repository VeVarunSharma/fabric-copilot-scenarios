# Sample prompt - Scenario 03

## Ready to copy prompt

```text
Generate a Microsoft Fabric-compatible PySpark notebook for IoT telemetry processing.

Target artifact:
- notebooks/iot-telemetry/telemetry_processing.ipynb

Input dataset:
- datasets/synthetic/iot-telemetry/

Requirements:
- Start with a parameter cell for process_date, source_path, curated_table, quarantine_table, and pipeline_run_id.
- Use an explicit StructType for device_id, event_ts, site_id, sensor_type, temperature_c, pressure_kpa, vibration_mms, battery_pct, firmware_version, and source_file.
- Read raw telemetry with the explicit schema. Do not rely on schema inference.
- Add ingestion_timestamp and pipeline_run_id metadata columns.
- Deduplicate on device_id plus event_ts, keeping the latest record by ingestion_timestamp.
- Quarantine rows that fail range checks: temperature_c outside -40 to 120, pressure_kpa outside 80 to 250, vibration_mms outside 0 to 75, or battery_pct outside 0 to 100.
- Use window functions to calculate a 15-minute rolling average temperature and a 1-hour maximum vibration per device.
- Write curated and quarantine outputs as Delta tables or Delta paths.
- Add structured logging and validation cells that show row counts and failed-rule counts.
- Keep workspace and lakehouse identifiers parameterized.
- Return a short notebook outline and the human review points.
```

## Follow-up prompts
- "Change the rolling metrics so they aggregate by site_id and sensor_type as well as device_id."
- "Add a late-arriving-data rule that flags events arriving more than 2 hours after event_ts."
- "Summarize the notebook sections for a pull request description."

## Acceptance criteria
- The notebook uses an explicit schema.
- Deduplication, range checks, windows, Delta writes, logging, and validation are all present.
- The response explains where a human needs to review thresholds and output locations.
