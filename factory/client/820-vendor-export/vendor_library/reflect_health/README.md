# Reflect Health Vendor Library

## What This Is
Reflect Health is a group health benefits administrator. This library contains all artifacts needed to produce their required inbound enrollment file format.

## What This Library Contains
| File | Purpose |
|------|---------|
| `data_dictionary.md` | Human-readable field reference from Reflect Health's spec |
| `column_metadata.yaml` | Machine-readable mirror of `reflect_health_schema` (183 rows) |
| `column_mapping.yaml` | Empty template: master_census → reflect_health column mappings |
| `capture_spec.yaml` | What we need to capture in census to feed this format |
| `export_spec.yaml` | How Reflect Health wants the file delivered |
| `invoice_spec.yaml` | Inbound invoice format (PENDING — sample not yet received) |
| `enum_values.yaml` | Enum lookup tables from the template reference sheets |

## How to Use
1. Run census intake to populate `master_census` and shards
2. Use `column_mapping.yaml` to JOIN master_census → reflect_health columns
3. Export per `export_spec.yaml` (CSV, UTF-8, pipe-delimited per Instructions sheet)
4. Deliver per transport spec in `export_spec.yaml`

## D1 Tables
- Target DB: `census`
- Migration: `src/migrations/001_d1_reflect_health.sql`
- Shards: `reflect_health_core` (46) | `reflect_health_employment` (46) | `reflect_health_benefits` (46) | `reflect_health_extended` (45)
- Schema table: `reflect_health_schema` (183 rows)
- Views: `v_reflect_health` | `v_reflect_health_required` | `v_reflect_health_schema`

## Key Facts
- 183 total columns (Full Template)
- 19 required columns (Minimum Template)
- Natural PK: `subscriber_number` (employee SSN, 9 digits)
- Instructions: DO NOT change header names without providing mapping
