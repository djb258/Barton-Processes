-- 001_d1_reflect_health.sql
-- Reflect Health inbound enrollment integration
-- Generated: 2026-04-20 | Source: inbound_template.xlsx
-- 183 columns | 4 shards | schema table | mapping table | 3 views

-- Shard: reflect_health_core (46 cols)
CREATE TABLE IF NOT EXISTS reflect_health_core (
  subscriber_number TEXT NOT NULL,
  employer TEXT,
  relationshipcode TEXT,
  memberlastname TEXT,
  memberfirstname TEXT,
  membermiddleinitial TEXT,
  addressline1 TEXT,
  addressline2 TEXT,
  city TEXT,
  state TEXT,
  zipcode TEXT,
  country TEXT,
  homephone TEXT,
  workphone TEXT,
  dateofbirth TEXT,
  emailaddress TEXT,
  gender TEXT,
  socialsecuritynumber TEXT,
  hireddate TEXT,
  dateofdeath TEXT,
  memberstatus TEXT,
  memberstatusdate TEXT,
  maritalstatus TEXT,
  retiredcode TEXT,
  smokercode TEXT,
  vipcode TEXT,
  clientlevelcode TEXT,
  groupnumber TEXT,
  grouplocationnumber TEXT,
  cobracode TEXT,
  groupeffectivedate TEXT,
  groupterminationdate TEXT,
  memberpaidthrudate TEXT,
  medicalcoveragetype TEXT,
  medicalcoveragetier TEXT,
  medicaleffectivedate TEXT,
  medicalterminationdate TEXT,
  dentalcoveragetype TEXT,
  dentalcoveragetier TEXT,
  dentaleffectivedate TEXT,
  dentalterminationdate TEXT,
  visioncoveragetype TEXT,
  visioncoveragetier TEXT,
  visioneffectivedate TEXT,
  visionterminationdate TEXT,
  disabilitycoveragetype TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (subscriber_number)
);

-- Shard: reflect_health_employment (46 cols)
CREATE TABLE IF NOT EXISTS reflect_health_employment (
  subscriber_number TEXT NOT NULL,
  disabilityeffectivedate TEXT,
  disabilityterminationdate TEXT,
  disabilitycoverageamount TEXT,
  flexpayrollperiod TEXT,
  flexcoveragetype TEXT,
  flexmedicalpayperiodcont TEXT,
  flexmedicalyearlytotal TEXT,
  flexeffectivedate TEXT,
  flexterminationdate TEXT,
  flexdependentpayperiodcont TEXT,
  flextranspayperiodcont TEXT,
  lifecoveragetype TEXT,
  lifeeffectivedate TEXT,
  lifeterminationdate TEXT,
  lifecoverageamount TEXT,
  adadcoveragetype TEXT,
  adadeffectivedate TEXT,
  adadterminationdate TEXT,
  adadcoverageamount TEXT,
  hracoveragetype TEXT,
  hraeffectivedate TEXT,
  hraterminationdate TEXT,
  preexistingexpirationdate TEXT,
  network1 TEXT,
  network1effectivedate TEXT,
  network2 TEXT,
  network2effectivedate TEXT,
  network3 TEXT,
  network3effectivedate TEXT,
  primarypcpid TEXT,
  primarypcpeffectivedate TEXT,
  payrollinternalcode TEXT,
  otherdata TEXT,
  otherdata2 TEXT,
  alternateid TEXT,
  rider01 TEXT,
  rider02 TEXT,
  rider03 TEXT,
  rider04 TEXT,
  rider05 TEXT,
  rider06 TEXT,
  rider07 TEXT,
  rider08 TEXT,
  rider09 TEXT,
  rider10 TEXT,
  medicaltermreason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (subscriber_number)
);

-- Shard: reflect_health_benefits (46 cols)
CREATE TABLE IF NOT EXISTS reflect_health_benefits (
  subscriber_number TEXT NOT NULL,
  dentaltermreason TEXT,
  visiontermreason TEXT,
  disabilitytermreason TEXT,
  flextermreason TEXT,
  lifetermreason TEXT,
  adadtermreason TEXT,
  hratermreason TEXT,
  hsatermreason TEXT,
  ltdtermreason TEXT,
  lifesptermreason TEXT,
  lifedptermreason TEXT,
  lifesuptermreason TEXT,
  lifesupsptermreason TEXT,
  lifesupdptermreason TEXT,
  adadsptermreason TEXT,
  adaddptermreason TEXT,
  adadsuptermreason TEXT,
  adadsupsptermreason TEXT,
  adadsupdptermreason TEXT,
  hsacoveragetype TEXT,
  hsaeffectivedate TEXT,
  hsaterminationdate TEXT,
  ltdcoveragetype TEXT,
  ltdeffectivedate TEXT,
  ltdterminationdate TEXT,
  ltdcoverageamount TEXT,
  lifespcoveragetype TEXT,
  lifespeffectivedate TEXT,
  lifespterminationdate TEXT,
  lifespcoverageamount TEXT,
  lifedpcoveragetype TEXT,
  lifedpeffectivedate TEXT,
  lifedpterminationdate TEXT,
  lifedpcoverageamount TEXT,
  lifesupcoveragetype TEXT,
  lifesupeffectivedate TEXT,
  lifesupterminationdate TEXT,
  lifesupcoverageamount TEXT,
  lifesupspcoveragetype TEXT,
  lifesupspeffectivedate TEXT,
  lifesupspterminationdate TEXT,
  lifesupspcoverageamount TEXT,
  lifesupdpcoveragetype TEXT,
  lifesupdpeffectivedate TEXT,
  lifesupdpterminationdate TEXT,
  lifesupdpcoverageamount TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (subscriber_number)
);

-- Shard: reflect_health_extended (45 cols)
CREATE TABLE IF NOT EXISTS reflect_health_extended (
  subscriber_number TEXT NOT NULL,
  adadspcoveragetype TEXT,
  adadspeffectivedate TEXT,
  adadspterminationdate TEXT,
  adadspcoverageamount TEXT,
  adaddpcoveragetype TEXT,
  adaddpeffectivedate TEXT,
  adaddpterminationdate TEXT,
  adaddpcoverageamount TEXT,
  adadsupcoveragetype TEXT,
  adadsupeffectivedate TEXT,
  adadsupterminationdate TEXT,
  adadsupcoverageamount TEXT,
  adadsupspcoveragetype TEXT,
  adadsupspeffectivedate TEXT,
  adadsupspterminationdate TEXT,
  adadsupspcoverageamount TEXT,
  adadsupdpcoveragetype TEXT,
  adadsupdpeffectivedate TEXT,
  adadsupdpterminationdate TEXT,
  adadsupdpcoverageamount TEXT,
  stdsupcoveragetype TEXT,
  stdsupeffectivedate TEXT,
  stdsupterminationdate TEXT,
  stdsupcoverageamount TEXT,
  ltdsupcoveragetype TEXT,
  ltdsupeffectivedate TEXT,
  ltdsupterminationdate TEXT,
  ltdsupcoverageamount TEXT,
  stdsuptermreason TEXT,
  ltdsuptermreason TEXT,
  cricoveragetype TEXT,
  cricoveragetier TEXT,
  crieffectivedate TEXT,
  criterminationdate TEXT,
  critermreason TEXT,
  idmcoveragetype TEXT,
  idmcoveragetier TEXT,
  idmeffectivedate TEXT,
  idmterminationdate TEXT,
  idmtermreason TEXT,
  rxpcoveragetype TEXT,
  rxpcoveragetier TEXT,
  rxpeffectivedate TEXT,
  rxpterminationdate TEXT,
  rxptermreason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (subscriber_number)
);

CREATE TABLE IF NOT EXISTS reflect_health_schema (
  column_id TEXT PRIMARY KEY,
  column_name TEXT NOT NULL,
  original_label TEXT NOT NULL,
  description TEXT,
  format TEXT,
  category TEXT,
  classification TEXT,
  required INTEGER DEFAULT 0,
  source_form TEXT DEFAULT 'reflect_health_inbound_template',
  shard_table TEXT
);

INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-001', 'employer', 'Employer', 'Employer', 'text', 'employment', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-002', 'subscribernumber', 'SubscriberNumber', 'The subscriber number is used to uniquely define an employee.  This is employees 9 digit social security number with or with out dashes.', 'ssn 9-digit', 'identity', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-003', 'relationshipcode', 'RelationshipCode', 'Identifies the relationship of the member to the subscriber.  Use: 1 for a subscriber, 2 for a spouse, 3 for a child, 4 for other', 'enum:1|2|3|4', 'identity', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-004', 'memberlastname', 'MemberLastName', "Member''s Last Name including SR, JR, etc. (without comma)", 'text', 'identity', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-005', 'memberfirstname', 'MemberFirstName', "Member''s formal first name.", 'text', 'identity', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-006', 'membermiddleinitial', 'MemberMiddleInitial', 'MemberMiddleInitial', 'text', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-007', 'addressline1', 'AddressLine1', 'Mailing Address line 1', 'text', 'contact', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-008', 'addressline2', 'AddressLine2', 'Mailing additional Address.  space if none.', 'text', 'contact', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-009', 'city', 'City', 'Mailing City', 'text', 'contact', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-010', 'state', 'State', 'Mailing state code.', 'text', 'contact', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-011', 'zipcode', 'ZipCode', 'Mailing zip code. Format as 99999-9999 or 99999)', 'text 5-or-9-digit', 'contact', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-012', 'country', 'Country', "Member''s country  Default is USA", 'text', 'contact', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-013', 'homephone', 'HomePhone', "Member''s 10 digit home phone number.", 'text', 'contact', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-014', 'workphone', 'WorkPhone', "Member''s 10 digit work phone number", 'text', 'contact', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-015', 'dateofbirth', 'DateOfBirth', "Member''s Birthday formatted as Any valid date format.", 'date YYYY-MM-DD', 'identity', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-016', 'emailaddress', 'EmailAddress', "Member''s E-Mail address", 'text', 'contact', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-017', 'gender', 'Gender', "The member''s gender, use:  F for a Female member, M for a Male member or U", 'enum:M|F|U', 'identity', 'PII', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-018', 'socialsecuritynumber', 'SocialSecurityNumber', 'Enter the 9 digit social security number of the member if known.  For the subscriber this should always be the same as the Subscriber Number.', 'ssn 9-digit', 'identity', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-019', 'hireddate', 'HiredDate', 'HiredDate', 'date YYYY-MM-DD', 'employment', 'Operational', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-020', 'dateofdeath', 'DateofDeath', 'DateofDeath', 'date YYYY-MM-DD', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-021', 'memberstatus', 'MemberStatus', 'Student or Handicapped Status, use S, H or blank', 'text', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-022', 'memberstatusdate', 'MemberStatusDate', 'Date on which Student or Handicapped status was last verified.', 'date YYYY-MM-DD', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-023', 'maritalstatus', 'MaritalStatus', "Member''s Marital Status  S for single, M for married, D for divorced, W for widowed", 'text', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-024', 'retiredcode', 'RetiredCode', "The member''s retired status:  Y for retired, N for not retired", 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-025', 'smokercode', 'SmokerCode', "The member''s smoker status:  Y for smoker, N for non-smoker", 'text', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-026', 'vipcode', 'VIPCode', 'VIP Member, use Y (yes) or N (no)', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-027', 'clientlevelcode', 'ClientLevelCode', 'Assigned by S&S; Please request if not given.', 'text', 'coverage', 'Operational', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-028', 'groupnumber', 'GroupNumber', 'Parent Group Code as setup with S&S.  Please request if not given.', 'text', 'coverage', 'Operational', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-029', 'grouplocationnumber', 'GroupLocationNumber', 'Group Location as setup wity S&S.  Please request if not given.', 'text', 'coverage', 'Operational', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-030', 'cobracode', 'CobraCode', "Cobra Benefits code  C for receiving Cobra, '' '' for not receiving", 'text', 'cobra', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-031', 'groupeffectivedate', 'GroupEffectiveDate', 'Effective date the member started in the group and location.', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-032', 'groupterminationdate', 'GroupTerminationDate', 'Date the member was terminated from coverage or from the group and location in fields 27 & 28.  If still active, please use 99991231 but can be blank.', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-033', 'memberpaidthrudate', 'MemberPaidThruDate', "Date the member''s coverages are paid up to (thru)", 'date YYYY-MM-DD', 'identity', 'PII', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-034', 'medicalcoveragetype', 'MedicalCoverageType', 'Level or Plan code for medical coverage.', 'enum:see_data_dictionary', 'medical', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-035', 'medicalcoveragetier', 'MedicalCoverageTier', 'Tier code for medical coverage', 'enum:see_data_dictionary', 'medical', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-036', 'medicaleffectivedate', 'MedicalEffectiveDate', 'Effective Date for the specific benefit coverage listed.  If the  information for determining group or benefit level changes, this date MUST reflect the change date of coverage. This date is used in the actual update program. Use Any valid date format.', 'date YYYY-MM-DD', 'medical', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-037', 'medicalterminationdate', 'MedicalTerminationDate', 'Required if member is terming.  Termination Date for the specific benefit coverage listed.', 'date YYYY-MM-DD', 'medical', 'PHI', 1, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-038', 'dentalcoveragetype', 'DentalCoverageType', 'DentalCoverageType', 'enum:see_data_dictionary', 'dental', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-039', 'dentalcoveragetier', 'DentalCoverageTier', 'DentalCoverageTier', 'enum:see_data_dictionary', 'dental', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-040', 'dentaleffectivedate', 'DentalEffectiveDate', 'DentalEffectiveDate', 'date YYYY-MM-DD', 'dental', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-041', 'dentalterminationdate', 'DentalTerminationDate', 'DentalTerminationDate', 'date YYYY-MM-DD', 'dental', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-042', 'visioncoveragetype', 'VisionCoverageType', 'VisionCoverageType', 'enum:see_data_dictionary', 'vision', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-043', 'visioncoveragetier', 'VisionCoverageTier', 'VisionCoverageTier', 'enum:see_data_dictionary', 'vision', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-044', 'visioneffectivedate', 'VisionEffectiveDate', 'VisionEffectiveDate', 'date YYYY-MM-DD', 'vision', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-045', 'visionterminationdate', 'VisionTerminationDate', 'VisionTerminationDate', 'date YYYY-MM-DD', 'vision', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-046', 'disabilitycoveragetype', 'DisabilityCoverageType', 'DisabilityCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_core');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-047', 'disabilityeffectivedate', 'DisabilityEffectiveDate', 'DisabilityEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-048', 'disabilityterminationdate', 'DisabilityTerminationDate', 'DisabilityTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-049', 'disabilitycoverageamount', 'DisabilityCoverageAmount', 'DisabilityCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-050', 'flexpayrollperiod', 'FlexPayrollPeriod', 'FlexPayrollPeriod', 'text', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-051', 'flexcoveragetype', 'FlexCoverageType', 'FlexCoverageType', 'enum:see_data_dictionary', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-052', 'flexmedicalpayperiodcont', 'FlexMedicalPayPeriodCont', 'FlexMedicalPayPeriodCont', 'text', 'medical', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-053', 'flexmedicalyearlytotal', 'FlexMedicalYearlyTotal', 'FlexMedicalYearlyTotal', 'text', 'medical', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-054', 'flexeffectivedate', 'FlexEffectiveDate', 'FlexEffectiveDate', 'date YYYY-MM-DD', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-055', 'flexterminationdate', 'FlexTerminationDate', 'FlexTerminationDate', 'date YYYY-MM-DD', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-056', 'flexdependentpayperiodcont', 'FlexDependentPayPeriodCont', 'FlexDependentPayPeriodCont', 'text', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-057', 'flextranspayperiodcont', 'FlexTransPayPeriodCont', 'FlexTransPayPeriodCont', 'text', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-058', 'lifecoveragetype', 'LifeCoverageType', 'LifeCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-059', 'lifeeffectivedate', 'LifeEffectiveDate', 'LifeEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-060', 'lifeterminationdate', 'LifeTerminationDate', 'LifeTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-061', 'lifecoverageamount', 'LifeCoverageAmount', 'LifeCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-062', 'adadcoveragetype', 'ADADCoverageType', 'ADADCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-063', 'adadeffectivedate', 'ADADEffectiveDate', 'ADADEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-064', 'adadterminationdate', 'ADADTerminationDate', 'ADADTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-065', 'adadcoverageamount', 'ADADCoverageAmount', 'ADADCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-066', 'hracoveragetype', 'HRACoverageType', 'HRACoverageType', 'enum:see_data_dictionary', 'hra', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-067', 'hraeffectivedate', 'HRAEffectiveDate', 'HRAEffectiveDate', 'date YYYY-MM-DD', 'hra', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-068', 'hraterminationdate', 'HRATerminationDate', 'HRATerminationDate', 'date YYYY-MM-DD', 'hra', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-069', 'preexistingexpirationdate', 'PreexistingExpirationDate', 'PreexistingExpirationDate', 'date YYYY-MM-DD', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-070', 'network1', 'Network1', 'Network/PPO', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-071', 'network1effectivedate', 'Network1EffectiveDate', 'Effective Date for network/PPO', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-072', 'network2', 'Network2', 'Network/PPO', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-073', 'network2effectivedate', 'Network2EffectiveDate', 'Effective Date for network/PPO', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-074', 'network3', 'Network3', 'Network/PPO', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-075', 'network3effectivedate', 'Network3EffectiveDate', 'Effective Date for network/PPO', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-076', 'primarypcpid', 'PrimaryPCPID', "This is the primary PCP''s ID or Tax ID  **NOTE:  If PCP changes then current MED plan terminates.", 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-077', 'primarypcpeffectivedate', 'PrimaryPCPEffectiveDate', 'This is the effective date of the primary PCP and/or primary provider organization.  Use the Any valid date format.', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-078', 'payrollinternalcode', 'PayrollInternalCode', 'PayrollInternalCode', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-079', 'otherdata', 'OtherData', 'Additional information that needs to be conveyed', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-080', 'otherdata2', 'OtherData2', 'Additional information that needs to be conveyed.', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-081', 'alternateid', 'AlternateID', 'Unique (per person) alternate id to be used for identification', 'text', 'metadata', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-082', 'rider01', 'Rider01', 'Rider01', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-083', 'rider02', 'Rider02', 'Rider02', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-084', 'rider03', 'Rider03', 'Rider03', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-085', 'rider04', 'Rider04', 'Rider04', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-086', 'rider05', 'Rider05', 'Rider05', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-087', 'rider06', 'Rider06', 'Rider06', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-088', 'rider07', 'Rider07', 'Rider07', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-089', 'rider08', 'Rider08', 'Rider08', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-090', 'rider09', 'Rider09', 'Rider09', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-091', 'rider10', 'Rider10', 'Rider10', 'text', 'rider', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-092', 'medicaltermreason', 'MedicalTermReason', 'Medical Termination of Coverage Reason.', 'text', 'medical', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_employment');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-093', 'dentaltermreason', 'DentalTermReason', 'Termination of Coverage Reason.', 'text', 'dental', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-094', 'visiontermreason', 'VisionTermReason', 'Termination of Coverage Reason.', 'text', 'vision', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-095', 'disabilitytermreason', 'DisabilityTermReason', 'DisabilityTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-096', 'flextermreason', 'FlexTermReason', 'FlexTermReason', 'text', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-097', 'lifetermreason', 'LifeTermReason', 'LifeTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-098', 'adadtermreason', 'ADADTermReason', 'ADADTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-099', 'hratermreason', 'HRATermReason', 'HRATermReason', 'text', 'hra', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-100', 'hsatermreason', 'HSATermReason', 'HSATermReason', 'text', 'hsa', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-101', 'ltdtermreason', 'LTDTermReason', 'LTDTermReason', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-102', 'lifesptermreason', 'LifeSpTermReason', 'LifeSpTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-103', 'lifedptermreason', 'LifeDpTermReason', 'LifeDpTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-104', 'lifesuptermreason', 'LifeSupTermReason', 'LifeSupTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-105', 'lifesupsptermreason', 'LifeSupSpTermReason', 'LifeSupSpTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-106', 'lifesupdptermreason', 'LifeSupDpTermReason', 'LifeSupDpTermReason', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-107', 'adadsptermreason', 'ADADSpTermReason', 'ADADSpTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-108', 'adaddptermreason', 'ADADDpTermReason', 'ADADDpTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-109', 'adadsuptermreason', 'ADADSupTermReason', 'ADADSupTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-110', 'adadsupsptermreason', 'ADADSupSpTermReason', 'ADADSupSpTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-111', 'adadsupdptermreason', 'ADADSupDpTermReason', 'ADADSupDpTermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-112', 'hsacoveragetype', 'HSACoverageType', 'HSACoverageType', 'enum:see_data_dictionary', 'hsa', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-113', 'hsaeffectivedate', 'HSAEffectiveDate', 'HSAEffectiveDate', 'date YYYY-MM-DD', 'hsa', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-114', 'hsaterminationdate', 'HSATerminationDate', 'HSATerminationDate', 'date YYYY-MM-DD', 'hsa', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-115', 'ltdcoveragetype', 'LTDCoverageType', 'LTDCoverageType', 'enum:see_data_dictionary', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-116', 'ltdeffectivedate', 'LTDEffectiveDate', 'LTDEffectiveDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-117', 'ltdterminationdate', 'LTDTerminationDate', 'LTDTerminationDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-118', 'ltdcoverageamount', 'LTDCoverageAmount', 'LTDCoverageAmount', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-119', 'lifespcoveragetype', 'LifeSpCoverageType', 'LifeSpCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-120', 'lifespeffectivedate', 'LifeSpEffectiveDate', 'LifeSpEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-121', 'lifespterminationdate', 'LifeSpTerminationDate', 'LifeSpTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-122', 'lifespcoverageamount', 'LifeSpCoverageAmount', 'LifeSpCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-123', 'lifedpcoveragetype', 'LifeDpCoverageType', 'LifeDpCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-124', 'lifedpeffectivedate', 'LifeDpEffectiveDate', 'LifeDpEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-125', 'lifedpterminationdate', 'LifeDpTerminationDate', 'LifeDpTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-126', 'lifedpcoverageamount', 'LifeDpCoverageAmount', 'LifeDpCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-127', 'lifesupcoveragetype', 'LifeSupCoverageType', 'LifeSupCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-128', 'lifesupeffectivedate', 'LifeSupEffectiveDate', 'LifeSupEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-129', 'lifesupterminationdate', 'LifeSupTerminationDate', 'LifeSupTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-130', 'lifesupcoverageamount', 'LifeSupCoverageAmount', 'LifeSupCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-131', 'lifesupspcoveragetype', 'LifeSupSpCoverageType', 'LifeSupSpCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-132', 'lifesupspeffectivedate', 'LifeSupSpEffectiveDate', 'LifeSupSpEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-133', 'lifesupspterminationdate', 'LifeSupSpTerminationDate', 'LifeSupSpTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-134', 'lifesupspcoverageamount', 'LifeSupSpCoverageAmount', 'LifeSupSpCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-135', 'lifesupdpcoveragetype', 'LifeSupDpCoverageType', 'LifeSupDpCoverageType', 'enum:see_data_dictionary', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-136', 'lifesupdpeffectivedate', 'LifeSupDpEffectiveDate', 'LifeSupDpEffectiveDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-137', 'lifesupdpterminationdate', 'LifeSupDpTerminationDate', 'LifeSupDpTerminationDate', 'date YYYY-MM-DD', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-138', 'lifesupdpcoverageamount', 'LifeSupDpCoverageAmount', 'LifeSupDpCoverageAmount', 'text', 'life_add', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_benefits');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-139', 'adadspcoveragetype', 'ADADSpCoverageType', 'ADADSpCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-140', 'adadspeffectivedate', 'ADADSpEffectiveDate', 'ADADSpEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-141', 'adadspterminationdate', 'ADADSpTerminationDate', 'ADADSpTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-142', 'adadspcoverageamount', 'ADADSpCoverageAmount', 'ADADSpCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-143', 'adaddpcoveragetype', 'ADADDpCoverageType', 'ADADDpCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-144', 'adaddpeffectivedate', 'ADADDpEffectiveDate', 'ADADDpEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-145', 'adaddpterminationdate', 'ADADDpTerminationDate', 'ADADDpTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-146', 'adaddpcoverageamount', 'ADADDpCoverageAmount', 'ADADDpCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-147', 'adadsupcoveragetype', 'ADADSupCoverageType', 'ADADSupCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-148', 'adadsupeffectivedate', 'ADADSupEffectiveDate', 'ADADSupEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-149', 'adadsupterminationdate', 'ADADSupTerminationDate', 'ADADSupTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-150', 'adadsupcoverageamount', 'ADADSupCoverageAmount', 'ADADSupCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-151', 'adadsupspcoveragetype', 'ADADSupSpCoverageType', 'ADADSupSpCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-152', 'adadsupspeffectivedate', 'ADADSupSpEffectiveDate', 'ADADSupSpEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-153', 'adadsupspterminationdate', 'ADADSupSpTerminationDate', 'ADADSupSpTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-154', 'adadsupspcoverageamount', 'ADADSupSpCoverageAmount', 'ADADSupSpCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-155', 'adadsupdpcoveragetype', 'ADADSupDpCoverageType', 'ADADSupDpCoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-156', 'adadsupdpeffectivedate', 'ADADSupDpEffectiveDate', 'ADADSupDpEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-157', 'adadsupdpterminationdate', 'ADADSupDpTerminationDate', 'ADADSupDpTerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-158', 'adadsupdpcoverageamount', 'ADADSupDpCoverageAmount', 'ADADSupDpCoverageAmount', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-159', 'stdsupcoveragetype', 'STDSupCoverageType', 'STDSupCoverageType', 'enum:see_data_dictionary', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-160', 'stdsupeffectivedate', 'STDSupEffectiveDate', 'STDSupEffectiveDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-161', 'stdsupterminationdate', 'STDSupTerminationDate', 'STDSupTerminationDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-162', 'stdsupcoverageamount', 'STDSupCoverageAmount', 'STDSupCoverageAmount', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-163', 'ltdsupcoveragetype', 'LTDSupCoverageType', 'LTDSupCoverageType', 'enum:see_data_dictionary', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-164', 'ltdsupeffectivedate', 'LTDSupEffectiveDate', 'LTDSupEffectiveDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-165', 'ltdsupterminationdate', 'LTDSupTerminationDate', 'LTDSupTerminationDate', 'date YYYY-MM-DD', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-166', 'ltdsupcoverageamount', 'LTDSupCoverageAmount', 'LTDSupCoverageAmount', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-167', 'stdsuptermreason', 'STDSupTermReason', 'STDSupTermReason', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-168', 'ltdsuptermreason', 'LTDSupTermReason', 'LTDSupTermReason', 'text', 'std_ltd', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-169', 'cricoveragetype', 'CRICoverageType', 'CRICoverageType', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-170', 'cricoveragetier', 'CRICoverageTier', 'CRICoverageTier', 'enum:see_data_dictionary', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-171', 'crieffectivedate', 'CRIEffectiveDate', 'CRIEffectiveDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-172', 'criterminationdate', 'CRITerminationDate', 'CRITerminationDate', 'date YYYY-MM-DD', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-173', 'critermreason', 'CRITermReason', 'CRITermReason', 'text', 'coverage', 'Operational', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-174', 'idmcoveragetype', 'IDMCoverageType', 'IDMCoverageType', 'enum:see_data_dictionary', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-175', 'idmcoveragetier', 'IDMCoverageTier', 'IDMCoverageTier', 'enum:see_data_dictionary', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-176', 'idmeffectivedate', 'IDMEffectiveDate', 'IDMEffectiveDate', 'date YYYY-MM-DD', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-177', 'idmterminationdate', 'IDMTerminationDate', 'IDMTerminationDate', 'date YYYY-MM-DD', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-178', 'idmtermreason', 'IDMTermReason', 'IDMTermReason', 'text', 'flex', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-179', 'rxpcoveragetype', 'RXPCoverageType', 'RXPCoverageType', 'enum:see_data_dictionary', 'rx', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-180', 'rxpcoveragetier', 'RXPCoverageTier', 'RXPCoverageTier', 'enum:see_data_dictionary', 'rx', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-181', 'rxpeffectivedate', 'RXPEffectiveDate', 'RXPEffectiveDate', 'date YYYY-MM-DD', 'rx', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-182', 'rxpterminationdate', 'RXPTerminationDate', 'RXPTerminationDate', 'date YYYY-MM-DD', 'rx', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');
INSERT OR IGNORE INTO reflect_health_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES ('RH-183', 'rxptermreason', 'RXPTermReason', 'RXPTermReason', 'text', 'rx', 'PHI', 0, 'reflect_health_inbound_template', 'reflect_health_extended');

CREATE TABLE IF NOT EXISTS vendor_column_mapping (
  mapping_id TEXT PRIMARY KEY,
  source_vendor TEXT NOT NULL,
  source_column_id TEXT NOT NULL,
  target_vendor TEXT NOT NULL,
  target_column_id TEXT NOT NULL,
  transform TEXT NOT NULL DEFAULT 'passthrough',
  transform_logic TEXT,
  confidence TEXT NOT NULL DEFAULT 'review',
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(source_vendor, source_column_id, target_vendor, target_column_id)
);

CREATE VIEW IF NOT EXISTS v_reflect_health AS
SELECT
  c.subscriber_number,
  c.employer,
  c.relationshipcode,
  c.memberlastname,
  c.memberfirstname,
  c.membermiddleinitial,
  c.addressline1,
  c.addressline2,
  c.city,
  c.state,
  c.zipcode,
  c.country,
  c.homephone,
  c.workphone,
  c.dateofbirth,
  c.emailaddress,
  c.gender,
  c.socialsecuritynumber,
  c.hireddate,
  c.dateofdeath,
  c.memberstatus,
  c.memberstatusdate,
  c.maritalstatus,
  c.retiredcode,
  c.smokercode,
  c.vipcode,
  c.clientlevelcode,
  c.groupnumber,
  c.grouplocationnumber,
  c.cobracode,
  c.groupeffectivedate,
  c.groupterminationdate,
  c.memberpaidthrudate,
  c.medicalcoveragetype,
  c.medicalcoveragetier,
  c.medicaleffectivedate,
  c.medicalterminationdate,
  c.dentalcoveragetype,
  c.dentalcoveragetier,
  c.dentaleffectivedate,
  c.dentalterminationdate,
  c.visioncoveragetype,
  c.visioncoveragetier,
  c.visioneffectivedate,
  c.visionterminationdate,
  c.disabilitycoveragetype,
  e.disabilityeffectivedate,
  e.disabilityterminationdate,
  e.disabilitycoverageamount,
  e.flexpayrollperiod,
  e.flexcoveragetype,
  e.flexmedicalpayperiodcont,
  e.flexmedicalyearlytotal,
  e.flexeffectivedate,
  e.flexterminationdate,
  e.flexdependentpayperiodcont,
  e.flextranspayperiodcont,
  e.lifecoveragetype,
  e.lifeeffectivedate,
  e.lifeterminationdate,
  e.lifecoverageamount,
  e.adadcoveragetype,
  e.adadeffectivedate,
  e.adadterminationdate,
  e.adadcoverageamount,
  e.hracoveragetype,
  e.hraeffectivedate,
  e.hraterminationdate,
  e.preexistingexpirationdate,
  e.network1,
  e.network1effectivedate,
  e.network2,
  e.network2effectivedate,
  e.network3,
  e.network3effectivedate,
  e.primarypcpid,
  e.primarypcpeffectivedate,
  e.payrollinternalcode,
  e.otherdata,
  e.otherdata2,
  e.alternateid,
  e.rider01,
  e.rider02,
  e.rider03,
  e.rider04,
  e.rider05,
  e.rider06,
  e.rider07,
  e.rider08,
  e.rider09,
  e.rider10,
  e.medicaltermreason,
  b.dentaltermreason,
  b.visiontermreason,
  b.disabilitytermreason,
  b.flextermreason,
  b.lifetermreason,
  b.adadtermreason,
  b.hratermreason,
  b.hsatermreason,
  b.ltdtermreason,
  b.lifesptermreason,
  b.lifedptermreason,
  b.lifesuptermreason,
  b.lifesupsptermreason,
  b.lifesupdptermreason,
  b.adadsptermreason,
  b.adaddptermreason,
  b.adadsuptermreason,
  b.adadsupsptermreason,
  b.adadsupdptermreason,
  b.hsacoveragetype,
  b.hsaeffectivedate,
  b.hsaterminationdate,
  b.ltdcoveragetype,
  b.ltdeffectivedate,
  b.ltdterminationdate,
  b.ltdcoverageamount,
  b.lifespcoveragetype,
  b.lifespeffectivedate,
  b.lifespterminationdate,
  b.lifespcoverageamount,
  b.lifedpcoveragetype,
  b.lifedpeffectivedate,
  b.lifedpterminationdate,
  b.lifedpcoverageamount,
  b.lifesupcoveragetype,
  b.lifesupeffectivedate,
  b.lifesupterminationdate,
  b.lifesupcoverageamount,
  b.lifesupspcoveragetype,
  b.lifesupspeffectivedate,
  b.lifesupspterminationdate,
  b.lifesupspcoverageamount,
  b.lifesupdpcoveragetype,
  b.lifesupdpeffectivedate,
  b.lifesupdpterminationdate,
  b.lifesupdpcoverageamount,
  x.adadspcoveragetype,
  x.adadspeffectivedate,
  x.adadspterminationdate,
  x.adadspcoverageamount,
  x.adaddpcoveragetype,
  x.adaddpeffectivedate,
  x.adaddpterminationdate,
  x.adaddpcoverageamount,
  x.adadsupcoveragetype,
  x.adadsupeffectivedate,
  x.adadsupterminationdate,
  x.adadsupcoverageamount,
  x.adadsupspcoveragetype,
  x.adadsupspeffectivedate,
  x.adadsupspterminationdate,
  x.adadsupspcoverageamount,
  x.adadsupdpcoveragetype,
  x.adadsupdpeffectivedate,
  x.adadsupdpterminationdate,
  x.adadsupdpcoverageamount,
  x.stdsupcoveragetype,
  x.stdsupeffectivedate,
  x.stdsupterminationdate,
  x.stdsupcoverageamount,
  x.ltdsupcoveragetype,
  x.ltdsupeffectivedate,
  x.ltdsupterminationdate,
  x.ltdsupcoverageamount,
  x.stdsuptermreason,
  x.ltdsuptermreason,
  x.cricoveragetype,
  x.cricoveragetier,
  x.crieffectivedate,
  x.criterminationdate,
  x.critermreason,
  x.idmcoveragetype,
  x.idmcoveragetier,
  x.idmeffectivedate,
  x.idmterminationdate,
  x.idmtermreason,
  x.rxpcoveragetype,
  x.rxpcoveragetier,
  x.rxpeffectivedate,
  x.rxpterminationdate,
  x.rxptermreason
FROM reflect_health_core c
LEFT JOIN reflect_health_employment e ON c.subscriber_number = e.subscriber_number
LEFT JOIN reflect_health_benefits b ON c.subscriber_number = b.subscriber_number
LEFT JOIN reflect_health_extended x ON c.subscriber_number = x.subscriber_number;

CREATE VIEW IF NOT EXISTS v_reflect_health_required AS
SELECT
  c.subscribernumber,
  c.relationshipcode,
  c.memberlastname,
  c.memberfirstname,
  c.addressline1,
  c.city,
  c.state,
  c.zipcode,
  c.dateofbirth,
  c.gender,
  c.socialsecuritynumber,
  c.hireddate,
  c.clientlevelcode,
  c.groupnumber,
  c.grouplocationnumber,
  c.medicalcoveragetype,
  c.medicalcoveragetier,
  c.medicaleffectivedate,
  c.medicalterminationdate
FROM reflect_health_core c
LEFT JOIN reflect_health_employment e ON c.subscriber_number = e.subscriber_number
LEFT JOIN reflect_health_benefits b ON c.subscriber_number = b.subscriber_number
LEFT JOIN reflect_health_extended x ON c.subscriber_number = x.subscriber_number;

CREATE VIEW IF NOT EXISTS v_reflect_health_schema AS
SELECT * FROM reflect_health_schema ORDER BY column_id;
