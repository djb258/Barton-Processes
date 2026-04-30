# DOCTRINE - Process 840 Client Record Key
## Locked rules. Auditor enforces. Violations halt any cross-system client JOIN.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-840-01 | sovereign_id (company_unique_id in CL spine, sovereign_id in MC clients) is the ONLY valid cross-system join key for client records. No other field may be used as a cross-system identifier. | PROCESS-UT.md §6 JOIN CONTRACT; heir.yaml acceptance_criteria[0] | §8 stop — any JOIN via company_name, client_id, or ad-hoc key is a violation |
| D-840-02 | No fallback joins permitted. If sovereign_id is NULL or resolves to no row, the operation must HALT and log to the appropriate error table. No silent fallback to name-match or domain-match joins. | PROCESS-UT.md §6 JOIN CONTRACT; §8 Stop Conditions | §8 stop — fallback JOIN is an orphan risk; HALT and log |
| D-840-03 | CL spine (cl_company_identity) is the sovereign identity source. No system may write to cl_company_identity except the authorized seed/sync process. MC API reads from CL; CL does not receive writes from MC. | PROCESS-UT.md §9 PERMISSIONS Write Rules | §8 stop — unauthorized write to CL spine is a critical violation |
| D-840-04 | Every MC clients record must carry a non-NULL sovereign_id that resolves to a row in cl_company_identity before the record is considered valid. Records without sovereign_id are orphans and must be flagged immediately. | PROCESS-UT.md §8 INGEST CHECKLIST Stop Conditions; heir.yaml acceptance_criteria[1] | §8 stop — NULL sovereign_id on any clients row halts all downstream operations on that record |
| D-840-05 | Ingest order is MANDATORY: Step 1 = establish CL spine row, Step 2 = create MC clients row with sovereign_id from Step 1, Step 3 = add contacts. Steps cannot be reordered. No MC row before a CL row exists. | PROCESS-UT.md §8 INGEST CHECKLIST | §8 stop — out-of-order ingest is a foreign key violation; HALT |
| D-840-06 | client_id (MC-internal PK) must never be used as a cross-system identifier. It is scoped to svg-d1-client only. All cross-system references use sovereign_id. | PROCESS-UT.md §5 CONTRACT §5d Internal PKs; heir.yaml acceptance_criteria[2] | pre-flight — any external system referencing client_id instead of sovereign_id is a design violation |
| D-840-07 | Contacts are MC-only. CL spine does not hold person-level data. No attempt may be made to store contact-level fields in cl_company_identity. | PROCESS-UT.md §9 PERMISSIONS Write Rules | §8 stop — contact write to CL spine is a schema violation |
| D-840-08 | Interactions are MC-only and append-only in practice. CL spine does not log touchpoints. No deletion of client_interactions rows except by explicit admin action with audit trail. | PROCESS-UT.md §9 PERMISSIONS Write Rules | §8 stop — deletion of interaction records without audit trail is a compliance violation |
| D-840-09 | To revoke/offboard a client: set lifecycle_stage = 'churned' and orbt_mode = 'REPAIR' on the MC clients row. Never delete from CL spine. The CL spine row is the permanent sovereign record. | PROCESS-UT.md §8 INGEST CHECKLIST Kill Switch | §8 stop — hard delete from CL spine is irreversible; HALT |
| D-840-10 | Any new system that holds client data MUST declare its field mappings against this KEY before going live. New fields not present in this KEY must trigger a KEY update that back-propagates to all consumers. | PROCESS-UT.md §4 IMO Circle; heir.yaml acceptance_criteria[3] | pre-flight — undeclared field mapping is a doctrine violation; system cannot go live without KEY registration |

## Cross-references
- UT §6 JOIN CONTRACT references rules D-840-01, D-840-02, D-840-03, D-840-06 by ID
- UT §8 INGEST CHECKLIST cites D-840-04 (NULL sovereign_id), D-840-05 (ingest order), D-840-09 (kill switch)
- UT §9 PERMISSIONS cites D-840-03 (CL spine write), D-840-07 (contacts), D-840-08 (interactions)
- UT §5 CONTRACT §5d Internal PKs grounds D-840-06 (client_id scope)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | v2 KEY.md + Bedrock + Atlas §1.6 Atlas System bundle |
| Rule Count | 10 (D-840-01 through D-840-10) |
