# Dataset onboarding

Candidate discovery portals (not yet imported datasets): WHO Global Health Observatory https://www.who.int/data/gho ; India Open Government Data https://www.data.gov.in/ ; CDC data and statistics https://www.cdc.gov/datastatistics/ ; HealthData.gov https://healthdata.gov/ .

Verify exact dataset, publisher, license, geography, time grain, reporting delay and refresh cadence before ingestion. Register provenance in dataset_sources. Normalize observation date, time grain, geography, disease code/name, aggregate case/admission count, source record ID and estimated/imputed flag.

Quality checks: parse dates explicitly; deduplicate using documented keys; reject negative counts; distinguish zero from missing; investigate implausible jumps; log rejected records; preserve source files and transformation versions; never combine incompatible time grains/geographies without a documented aggregation rule.

No external dataset has been imported yet. The dashboard remains in preview until data is selected and validated.