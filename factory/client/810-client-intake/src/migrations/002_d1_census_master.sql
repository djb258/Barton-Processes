-- ═══════════════════════════════════════════════════════════════════════════
-- 002_d1_census_master.sql
-- Source shape: JotForm-style benefit enrollment intake (Cochran 2026-04-22)
-- D1 SQLite column limit (~60 per table) requires sharding the 136-column
-- wide census across 3 satellite tables joined by submission_id.
-- All columns TEXT for permissive intake; type coercion happens in views.
--
-- Shard layout:
--   census_identity     — CEN-001..CEN-050  (identity, contact, employment, metadata)
--   census_coverage     — CEN-051..CEN-082  (coverage elections, premiums, prescriptions)
--   census_dependents   — CEN-083..CEN-136  (Dep 1-5, signatures, waiver, auth)
-- ═══════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────
-- SHARD 1: identity, contact, employment, enrollment trigger — CEN-001..050
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS census_identity (
  submission_id                     TEXT PRIMARY KEY,
  first_name                        TEXT,
  last_name                         TEXT,
  submission_date                   TEXT,
  company                           TEXT,
  division                          TEXT,
  health_provided_by                TEXT,
  health_policy_number              TEXT,
  dental_provided_by                TEXT,
  dental_policy_number              TEXT,
  vision_provided_by                TEXT,
  vision_policy_number              TEXT,
  ltd_provided_by                   TEXT,
  life_insurance_provided_by        TEXT,
  group_life_policy_name            TEXT,
  group_life_policy_number          TEXT,
  benefit_deduction_frequency       TEXT,
  enroller                          TEXT,
  enrollment_reason                 TEXT,
  change_effective_date             TEXT,
  change_reason                     TEXT,
  add_dependents_due_to             TEXT,
  delete_dependents_due_to          TEXT,
  add_update_dependent_information  TEXT,
  date_of_termination               TEXT,
  reason_for_termination            TEXT,
  medical_termination_date          TEXT,
  dental_termination_date           TEXT,
  vision_termination_date           TEXT,
  group_life_termination_date       TEXT,
  std_ltd_termination_date          TEXT,
  other_change_reason               TEXT,
  relationship                      TEXT,
  relationship_dep_code             TEXT,
  employee_ssn                      TEXT,
  employee_birthday                 TEXT,
  employee_gender                   TEXT,
  is_employee_smoker                TEXT,
  home_address                      TEXT,
  city                              TEXT,
  state                             TEXT,
  zip                               TEXT,
  email_address                     TEXT,
  cell_phone_number                 TEXT,
  home_phone_number                 TEXT,
  work_phone                        TEXT,
  is_spouse_employed                TEXT,
  is_health_offered_by_spouse_employer TEXT,
  is_hdhp_hsa                       TEXT,
  is_health_offered_for_dependents  TEXT,
  created_at                        TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at                        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ci_ssn            ON census_identity(employee_ssn);
CREATE INDEX IF NOT EXISTS idx_ci_company        ON census_identity(company);
CREATE INDEX IF NOT EXISTS idx_ci_submission_date ON census_identity(submission_date);

-- ─────────────────────────────────────────────────────────────────────────
-- SHARD 2: coverage flags, elections, premiums, prescriptions — CEN-051..082
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS census_coverage (
  submission_id                     TEXT PRIMARY KEY,
  has_other_health_insurance        TEXT,
  type_of_coverage                  TEXT,
  type_of_insurance                 TEXT,
  major_medical_coverage            TEXT,
  medical_effective_date            TEXT,
  had_prior_dental_coverage         TEXT,
  dental_coverage                   TEXT,
  dental_effective_date             TEXT,
  dental_plan_details               TEXT,
  had_prior_vision_coverage         TEXT,
  vision_coverage                   TEXT,
  vision_effective_date             TEXT,
  vision_plan_details               TEXT,
  employee_medical_premium          TEXT,
  employee_vision_premium           TEXT,
  employee_dental_premium           TEXT,
  total_employee_health_premium     TEXT,
  life_add_provided_by              TEXT,
  ltd_election                      TEXT,
  employee_class                    TEXT,
  group_life_coverage_status        TEXT,
  group_life_effective_date         TEXT,
  life_insurance_plan_details       TEXT,
  beneficiary                       TEXT,
  beneficiary_address               TEXT,
  beneficiary_birthday              TEXT,
  std_coverage                      TEXT,
  std_ltd_effective_date            TEXT,
  major_medical_plan_details        TEXT,
  std_ltd_plan_details              TEXT,
  has_current_prescriptions         TEXT,
  current_prescriptions_detail      TEXT,
  disenroll_benefits                TEXT,
  department                        TEXT,
  employee_date_of_hire             TEXT,
  state_of_employment               TEXT,
  hourly_or_salary                  TEXT,
  employee_yearly_salary_or_rate    TEXT,
  hours_per_week                    TEXT,
  marital_status                    TEXT,
  created_at                        TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at                        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cc_submission_id ON census_coverage(submission_id);

-- ─────────────────────────────────────────────────────────────────────────
-- SHARD 3: Dep 1-5, signatures, auth — CEN-083..136
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS census_dependents (
  submission_id     TEXT PRIMARY KEY,
  dep1_action       TEXT,
  dep1_dep_code     TEXT,
  dep1_first_name   TEXT,
  dep1_last_name    TEXT,
  dep1_gender       TEXT,
  dep1_relationship TEXT,
  dep1_ssn          TEXT,
  dep1_birthday     TEXT,
  dep2_action       TEXT,
  dep2_dep_code     TEXT,
  dep2_first_name   TEXT,
  dep2_last_name    TEXT,
  dep2_gender       TEXT,
  dep2_relationship TEXT,
  dep2_ssn          TEXT,
  dep2_birthday     TEXT,
  dep3_action       TEXT,
  dep3_dep_code     TEXT,
  dep3_first_name   TEXT,
  dep3_last_name    TEXT,
  dep3_gender       TEXT,
  dep3_relationship TEXT,
  dep3_ssn          TEXT,
  dep3_birthday     TEXT,
  dep4_action       TEXT,
  dep4_dep_code     TEXT,
  dep4_first_name   TEXT,
  dep4_last_name    TEXT,
  dep4_gender       TEXT,
  dep4_relationship TEXT,
  dep4_ssn          TEXT,
  dep4_birthday     TEXT,
  dep5_action       TEXT,
  dep5_dep_code     TEXT,
  dep5_first_name   TEXT,
  dep5_last_name    TEXT,
  dep5_gender       TEXT,
  dep5_relationship TEXT,
  dep5_ssn          TEXT,
  dep5_birthday     TEXT,
  waiver_signature_date     TEXT,
  waiver_signature          TEXT,
  authorization_signed_date TEXT,
  authorization_signature   TEXT,
  created_at                TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at                TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cd_submission_id ON census_dependents(submission_id);

-- ─────────────────────────────────────────────────────────────────────────
-- Schema metadata table
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS master_census_schema (
  column_id       TEXT PRIMARY KEY,
  column_name     TEXT UNIQUE NOT NULL,
  original_label  TEXT NOT NULL,
  description     TEXT NOT NULL,
  format          TEXT NOT NULL,
  category        TEXT NOT NULL,
  classification  TEXT NOT NULL,
  required        INTEGER NOT NULL DEFAULT 0,
  source_form     TEXT NOT NULL DEFAULT 'cochran_2026_04_22',
  shard_table     TEXT NOT NULL DEFAULT 'census_identity',
  created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mcs_category       ON master_census_schema(category);
CREATE INDEX IF NOT EXISTS idx_mcs_classification ON master_census_schema(classification);
CREATE INDEX IF NOT EXISTS idx_mcs_shard          ON master_census_schema(shard_table);

-- ═══════════════════════════════════════════════════════════════════════════
-- Schema metadata rows — 136 rows, CEN-001 through CEN-136
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO master_census_schema (column_id, column_name, original_label, description, format, category, classification, required, source_form, shard_table) VALUES
('CEN-001','first_name','First Name','Employee or dependent first name','text','identity','PII',1,'cochran_2026_04_22','census_identity'),
('CEN-002','last_name','Last Name','Employee or dependent last name','text','identity','PII',1,'cochran_2026_04_22','census_identity'),
('CEN-003','submission_date','Submission Date','Date the enrollment form was submitted','date YYYY-MM-DD','metadata','Operational',1,'cochran_2026_04_22','census_identity'),
('CEN-004','company','Company','Name of the employer sponsoring the benefit plan','text','company','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-005','division','Division','Organizational division or business unit of the employee','text','company','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-006','health_provided_by','Health Provided By','Carrier or insurer providing the group health plan','text','medical','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-007','health_policy_number','Health Policy Number','Group policy number for the health plan','text','medical','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-008','dental_provided_by','Dental Provided By','Carrier or insurer providing the group dental plan','text','dental','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-009','dental_policy_number','Dental Policy Number','Group policy number for the dental plan','text','dental','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-010','vision_provided_by','Vision Provided By','Carrier or insurer providing the group vision plan','text','vision','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-011','vision_policy_number','Vision Policy Number','Group policy number for the vision plan','text','vision','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-012','ltd_provided_by','LTD Provided By','Carrier or insurer providing long-term disability coverage','text','std_ltd','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-013','life_insurance_provided_by','Life Insurance Provided By','Carrier or insurer providing the group life insurance plan','text','life_add','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-014','group_life_policy_name','Group Life Policy Name','Plan name for the group life/AD&D policy','text','life_add','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-015','group_life_policy_number','Group Life Policy Number','Policy number for the group life/AD&D plan','text','life_add','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-016','benefit_deduction_frequency','Benefit Deduction Frequency','Payroll deduction frequency for benefits (e.g., semi-monthly, monthly)','text','employment','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-017','enroller','Enroller','Name or ID of the benefits agent or broker who completed the enrollment','text','metadata','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-018','enrollment_reason','Enrollment Reason','Reason triggering this enrollment event (new hire, open enrollment, qualifying life event)','text','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-019','change_effective_date','Change Effective Date','Date the coverage change becomes effective','date YYYY-MM-DD','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-020','change_reason','Change Reason','Specific reason code or description for the benefit change','text','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-021','add_dependents_due_to','Add Dependents Due To:','Qualifying life event reason for adding dependents (e.g., marriage, birth)','text','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-022','delete_dependents_due_to','Delete dependents due to:','Qualifying life event reason for removing dependents (e.g., divorce, aging out)','text','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-023','add_update_dependent_information','Add/Update Dependent Information','Flag or note indicating dependent information is being added or updated on this submission','text','dependent','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-024','date_of_termination','Date of Termination','Date the employee''s employment ended — triggers benefit termination and COBRA eligibility','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-025','reason_for_termination','Reason for Termination','Reason the employment was terminated (voluntary, involuntary, retirement, etc.)','text','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-026','medical_termination_date','Medical Termination Date','Date medical coverage ends for the employee or covered dependents','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-027','dental_termination_date','Dental Termination Date','Date dental coverage ends','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-028','vision_termination_date','Vision Termination Date','Date vision coverage ends','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-029','group_life_termination_date','Group Life Termination Date','Date group life and AD&D coverage ends','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-030','std_ltd_termination_date','STD/LTD Termination Date','Date short-term and/or long-term disability coverage ends','date YYYY-MM-DD','termination','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-031','other_change_reason','Other Change Reason','Free-text explanation when the change reason does not fit a predefined category','text long','enrollment_reason','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-032','relationship','Relationship','Employee relationship to the primary insured or to any enrolled dependent','text','identity','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-033','relationship_dep_code','Relationship/DEP Code','Carrier DEP code identifying relationship type (SP=Spouse, CH=Child, DP=Domestic Partner)','text','identity','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-034','employee_ssn','Employee''s Social Security  Number','Employee 9-digit Social Security Number used for underwriting and eligibility verification','ssn 9-digit','identity','Identity',1,'cochran_2026_04_22','census_identity'),
('CEN-035','employee_birthday','Employee Birthday','Employee date of birth used for age-banded rating and eligibility determination','date YYYY-MM-DD','identity','PII',1,'cochran_2026_04_22','census_identity'),
('CEN-036','employee_gender','Employee Gender','Employee gender as recorded on the enrollment form (used for rating)','enum:male/female','identity','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-037','is_employee_smoker','Is Employee a smoker?','Flag indicating whether the employee uses tobacco products (affects premium rates at some carriers)','enum:yes/no/na','medical','PHI',0,'cochran_2026_04_22','census_identity'),
('CEN-038','home_address','Home Address','Employee residential street address','text','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-039','city','City','City of the employee residential address','text','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-040','state','State','State abbreviation of the employee residential address','state 2-letter','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-041','zip','Zip','ZIP code of the employee residential address','zip 5-digit','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-042','email_address','Email Address','Employee primary email address for benefit communications','email','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-043','cell_phone_number','Cell Phone Number','Employee mobile phone number','phone 10-digit','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-044','home_phone_number','Home Phone Number','Employee residential landline phone number','phone 10-digit','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-045','work_phone','Work Phone','Employee work phone number','phone 10-digit','contact','PII',0,'cochran_2026_04_22','census_identity'),
('CEN-046','is_spouse_employed','Is your spouse employed?','Flag indicating whether the employee spouse is currently employed — relevant for coordination of benefits','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-047','is_health_offered_by_spouse_employer','Is Health Insurance offered through the employer?','Flag indicating whether health insurance is available through the spouse employer (COB trigger)','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-048','is_hdhp_hsa','Is this a high deductible health plan with a Health Savings Account?','Flag: is the selected medical plan an HDHP that allows the employee to contribute to an HSA','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-049','is_health_offered_for_dependents','Is health insurance coverage offered through an employer for any of your dependents?','Flag indicating whether another employer offers health coverage to any enrolled dependents','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-050','has_other_health_insurance','Does Employee or any family member have other health insurance?','Flag indicating COB scenario — employee or a covered family member has additional health insurance elsewhere','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-051','type_of_coverage','Type of Coverage','Coverage tier elected — EE (Employee Only), ES (Employee+Spouse), EC (Employee+Child), FAM (Family)','text','medical','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-052','type_of_insurance','Type of Insurance','Insurance product type elected (HMO, PPO, EPO, HDHP, etc.)','text','medical','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-053','major_medical_coverage','Major Medical Coverage','Major medical plan name or carrier selected for this enrollment period','text','medical','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-054','medical_effective_date','Medical Effective Date','Date medical coverage becomes effective','date YYYY-MM-DD','medical','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-055','had_prior_dental_coverage','Did employee have coverage for dental with prior carrier','Flag indicating the employee had dental coverage with a previous carrier (creditable coverage for waiting periods)','enum:yes/no/na','dental','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-056','dental_coverage','Dental Coverage','Dental plan name or carrier selected for this enrollment period','text','dental','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-057','dental_effective_date','Dental Effective Date','Date dental coverage becomes effective','date YYYY-MM-DD','dental','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-058','dental_plan_details','Dental Plan Details','Detailed description of the dental plan benefits, network, or special terms','text long','dental','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-059','had_prior_vision_coverage','Did employee have coverage for vision with prior carrier','Flag indicating the employee had vision coverage with a previous carrier','enum:yes/no/na','vision','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-060','vision_coverage','Vision Coverage','Vision plan name or carrier selected for this enrollment period','text','vision','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-061','vision_effective_date','Vision Effective Date','Date vision coverage becomes effective','date YYYY-MM-DD','vision','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-062','vision_plan_details','Vision Plan Details','Detailed description of the vision plan benefits or network','text long','vision','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-063','employee_medical_premium','Employee Medical Premium','Employee-paid portion of the monthly medical premium','decimal 2dp','medical','Financial',0,'cochran_2026_04_22','census_coverage'),
('CEN-064','employee_vision_premium','Employee Vision Premium','Employee-paid portion of the monthly vision premium','decimal 2dp','vision','Financial',0,'cochran_2026_04_22','census_coverage'),
('CEN-065','employee_dental_premium','Employee Dental Premium','Employee-paid portion of the monthly dental premium','decimal 2dp','dental','Financial',0,'cochran_2026_04_22','census_coverage'),
('CEN-066','total_employee_health_premium','Total Employee Health Insurance Premium','Sum of all employee-paid benefit premiums for this enrollment','decimal 2dp','medical','Financial',0,'cochran_2026_04_22','census_coverage'),
('CEN-067','life_add_provided_by','Group Term Life AD&D Insurance Coverage--Provided By','Carrier providing group term life and AD&D coverage','text','life_add','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-068','ltd_election','LTD Election','Long-term disability benefit option elected by the employee (e.g., 60% of salary)','text','std_ltd','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-069','employee_class','Employee Class','Employee classification used for underwriting and eligibility (full-time, part-time, executive)','text','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-070','group_life_coverage_status','Group Life Coverage Status','Status of the employee group life coverage election (enrolled, waived, pending)','text','life_add','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-071','group_life_effective_date','Group Life Effective Date','Date group life and AD&D coverage becomes effective','date YYYY-MM-DD','life_add','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-072','life_insurance_plan_details','Life Insurance Plan Details','Detailed description of the group life/AD&D plan including benefit amounts and riders','text long','life_add','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-073','beneficiary','Beneficiary','Full name of the primary beneficiary designated by the employee for life insurance proceeds','text','beneficiary','PII',0,'cochran_2026_04_22','census_coverage'),
('CEN-074','beneficiary_address','Beneficiary Address','Mailing address of the designated beneficiary','text','beneficiary','PII',0,'cochran_2026_04_22','census_coverage'),
('CEN-075','beneficiary_birthday','Beneficiary Birthday','Date of birth of the designated beneficiary','date YYYY-MM-DD','beneficiary','PII',0,'cochran_2026_04_22','census_coverage'),
('CEN-076','std_coverage','STD Coverage','Short-term disability coverage option elected by the employee','text','std_ltd','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-077','std_ltd_effective_date','STD/LTD Effective Date','Date short-term and/or long-term disability coverage becomes effective','date YYYY-MM-DD','std_ltd','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-078','major_medical_plan_details','Major Medical Plan Details','Detailed description of the major medical plan including deductible, out-of-pocket max, and network','text long','medical','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-079','std_ltd_plan_details','STD/LTD  Plan Details','Detailed description of the STD/LTD plan including elimination period and benefit percentage','text long','std_ltd','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-080','has_current_prescriptions','Does the employee/dependent have any current prescriptions?','Flag indicating whether the employee or any covered dependent is currently taking prescription medications','enum:yes/no/na','prescriptions','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-081','current_prescriptions_detail','If yes\n please list all prescriptions currently being taken\n along with dosage if known.','Free-text list of current prescriptions and dosages for the employee and covered dependents','text long','prescriptions','PHI',0,'cochran_2026_04_22','census_coverage'),
('CEN-082','disenroll_benefits','Which benefits would you like to disenroll? Only select benefits the employee is enrolled in.','Benefits selected for disenrollment — employee must only select plans currently active','text long','disenroll','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-083','dep1_action','Dep 1 Add or Remove','Action for dependent 1: add, remove, or keep (enrollment form instruction)','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-084','dep1_dep_code','Dep 1 DEP Code','Carrier DEP relationship code for dependent 1 (SP, CH, DP)','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-085','dep1_first_name','Dep 1 First Name','First name of dependent 1','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-086','dep1_last_name','Dep 1 Last Name','Last name of dependent 1','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-087','dep1_gender','Dep 1 Gender','Gender of dependent 1 as recorded on the enrollment form','enum:male/female','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-088','dep1_relationship','Dep 1 Relationship','Relationship of dependent 1 to the employee (Spouse, Child, Domestic Partner)','enum:employee/spouse/child/domestic_partner','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-089','dep1_ssn','Dep 1 Social Security  Number','Social Security Number of dependent 1 required for eligibility verification','ssn 9-digit','dependent','Identity',0,'cochran_2026_04_22','census_dependents'),
('CEN-090','dep1_birthday','Dep 1 Birthday','Date of birth of dependent 1 used for age eligibility and rating','date YYYY-MM-DD','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-091','dep2_action','Dep 2 Add or Remove','Action for dependent 2: add, remove, or keep','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-092','dep2_dep_code','Dep 2 DEP Code','Carrier DEP relationship code for dependent 2','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-093','dep2_first_name','Dep 2 First Name','First name of dependent 2','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-094','dep2_last_name','Dep 2 Last Name','Last name of dependent 2','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-095','dep2_gender','Dep 2 Gender','Gender of dependent 2','enum:male/female','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-096','dep2_relationship','Dep 2 Relationship','Relationship of dependent 2 to the employee','enum:employee/spouse/child/domestic_partner','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-097','dep2_ssn','Dep 2 Social Security  Number','Social Security Number of dependent 2','ssn 9-digit','dependent','Identity',0,'cochran_2026_04_22','census_dependents'),
('CEN-098','dep2_birthday','Dep 2 Birthday','Date of birth of dependent 2','date YYYY-MM-DD','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-099','dep3_action','Dep 3 Add or Remove','Action for dependent 3: add, remove, or keep','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-100','dep3_dep_code','Dep 3 DEP Code','Carrier DEP relationship code for dependent 3','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-101','dep3_first_name','Dep 3 First Name','First name of dependent 3','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-102','dep3_last_name','Dep 3 Last Name','Last name of dependent 3','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-103','dep3_gender','Dep 3 Gender','Gender of dependent 3','enum:male/female','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-104','dep3_relationship','Dep 3 Relationship','Relationship of dependent 3 to the employee','enum:employee/spouse/child/domestic_partner','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-105','dep3_ssn','Dep 3 Social Security  Number','Social Security Number of dependent 3','ssn 9-digit','dependent','Identity',0,'cochran_2026_04_22','census_dependents'),
('CEN-106','dep3_birthday','Dep 3 Birthday','Date of birth of dependent 3','date YYYY-MM-DD','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-107','dep4_action','Dep 4 Add or Remove','Action for dependent 4: add, remove, or keep','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-108','dep4_dep_code','Dep 4 DEP Code','Carrier DEP relationship code for dependent 4','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-109','dep4_first_name','Dep 4 First Name','First name of dependent 4','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-110','dep4_last_name','Dep 4 Last Name','Last name of dependent 4','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-111','dep4_gender','Dep 4 Gender','Gender of dependent 4','enum:male/female','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-112','dep4_relationship','Dep 4 Relationship','Relationship of dependent 4 to the employee','enum:employee/spouse/child/domestic_partner','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-113','dep4_ssn','Dep 4 Social Security  Number','Social Security Number of dependent 4','ssn 9-digit','dependent','Identity',0,'cochran_2026_04_22','census_dependents'),
('CEN-114','dep4_birthday','Dep 4 Birthday','Date of birth of dependent 4','date YYYY-MM-DD','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-115','dep5_action','Dep 5 Add or Remove','Action for dependent 5: add, remove, or keep','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-116','dep5_dep_code','Dep 5 DEP Code','Carrier DEP relationship code for dependent 5','text','dependent','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-117','dep5_first_name','Dep 5 First Name','First name of dependent 5','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-118','dep5_last_name','Dep 5 Last Name','Last name of dependent 5','text','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-119','dep5_gender','Dep 5 Gender','Gender of dependent 5','enum:male/female','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-120','dep5_relationship','Dep 5 Relationship','Relationship of dependent 5 to the employee','enum:employee/spouse/child/domestic_partner','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-121','dep5_ssn','Dep 5 Social Security  Number','Social Security Number of dependent 5','ssn 9-digit','dependent','Identity',0,'cochran_2026_04_22','census_dependents'),
('CEN-122','dep5_birthday','Dep 5 Birthday','Date of birth of dependent 5','date YYYY-MM-DD','dependent','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-123','waiver_signature_date','Date Card is Signed (Waiver)','Date the employee signed the benefits waiver card','date YYYY-MM-DD','signature','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-124','waiver_signature','Waiver Signature','Employee electronic or written signature authorizing the waiver of elected benefits','text','signature','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-125','authorization_signed_date','Date Signed (Authorization)','Date the employee signed the authorization form','date YYYY-MM-DD','signature','Operational',0,'cochran_2026_04_22','census_dependents'),
('CEN-126','authorization_signature','Authorization Signature','Employee electronic or written signature on the enrollment authorization','text','signature','PII',0,'cochran_2026_04_22','census_dependents'),
('CEN-127','department','Department','Employee assigned department within the company','text','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-128','employee_date_of_hire','Employee Date of Hire','Date the employee was hired — determines benefits eligibility waiting period','date YYYY-MM-DD','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-129','state_of_employment','State of Employment','State where the employee performs work — may differ from residence and affects state-mandated benefits','state 2-letter','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-130','hourly_or_salary','Hourly or Salary','Compensation type: hourly or salaried — affects eligibility for certain benefit tiers','text','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-131','employee_yearly_salary_or_rate','Employee Yearly Salary or Per Hour Rate','Annual salary or hourly pay rate used for life insurance benefit calculation and underwriting','decimal 2dp','employment','Financial',0,'cochran_2026_04_22','census_coverage'),
('CEN-132','hours_per_week','Hours per week','Average hours worked per week — used to determine full-time vs. part-time status for benefits eligibility','integer','employment','Operational',0,'cochran_2026_04_22','census_coverage'),
('CEN-133','marital_status','Marital Status','Employee marital status — relevant for dependent eligibility and coverage elections','text','identity','PII',0,'cochran_2026_04_22','census_coverage'),
('CEN-134','is_spouse_employed_b','Is your spouse employed?','Second capture of spouse employment flag (duplicate field on source form — see CEN-046)','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-135','is_health_offered_by_employer','Is Health Insurance offered through the employer?','Second capture of employer health offer flag (duplicate field on source form — see CEN-047)','enum:yes/no/na','coverage_flag','Operational',0,'cochran_2026_04_22','census_identity'),
('CEN-136','submission_id','Submission ID','Unique identifier assigned by the form system per submission — primary key across all census shard tables','text','metadata','Operational',1,'cochran_2026_04_22','census_identity');

-- ═══════════════════════════════════════════════════════════════════════════
-- Initial views (join shards on submission_id)
-- ═══════════════════════════════════════════════════════════════════════════

-- Full denormalized read (join all 3 shards)
CREATE VIEW IF NOT EXISTS v_census AS
SELECT
  i.*,
  c.has_other_health_insurance, c.type_of_coverage, c.type_of_insurance,
  c.major_medical_coverage, c.medical_effective_date,
  c.had_prior_dental_coverage, c.dental_coverage, c.dental_effective_date, c.dental_plan_details,
  c.had_prior_vision_coverage, c.vision_coverage, c.vision_effective_date, c.vision_plan_details,
  c.employee_medical_premium, c.employee_vision_premium, c.employee_dental_premium,
  c.total_employee_health_premium, c.life_add_provided_by, c.ltd_election, c.employee_class,
  c.group_life_coverage_status, c.group_life_effective_date, c.life_insurance_plan_details,
  c.beneficiary, c.beneficiary_address, c.beneficiary_birthday,
  c.std_coverage, c.std_ltd_effective_date, c.major_medical_plan_details, c.std_ltd_plan_details,
  c.has_current_prescriptions, c.current_prescriptions_detail, c.disenroll_benefits,
  c.department, c.employee_date_of_hire, c.state_of_employment, c.hourly_or_salary,
  c.employee_yearly_salary_or_rate, c.hours_per_week, c.marital_status,
  d.dep1_action, d.dep1_dep_code, d.dep1_first_name, d.dep1_last_name, d.dep1_gender,
  d.dep1_relationship, d.dep1_ssn, d.dep1_birthday,
  d.dep2_action, d.dep2_dep_code, d.dep2_first_name, d.dep2_last_name, d.dep2_gender,
  d.dep2_relationship, d.dep2_ssn, d.dep2_birthday,
  d.dep3_action, d.dep3_dep_code, d.dep3_first_name, d.dep3_last_name, d.dep3_gender,
  d.dep3_relationship, d.dep3_ssn, d.dep3_birthday,
  d.dep4_action, d.dep4_dep_code, d.dep4_first_name, d.dep4_last_name, d.dep4_gender,
  d.dep4_relationship, d.dep4_ssn, d.dep4_birthday,
  d.dep5_action, d.dep5_dep_code, d.dep5_first_name, d.dep5_last_name, d.dep5_gender,
  d.dep5_relationship, d.dep5_ssn, d.dep5_birthday,
  d.waiver_signature_date, d.waiver_signature, d.authorization_signed_date, d.authorization_signature
FROM census_identity i
LEFT JOIN census_coverage  c ON c.submission_id = i.submission_id
LEFT JOIN census_dependents d ON d.submission_id = i.submission_id;

-- PII-only slice
CREATE VIEW IF NOT EXISTS v_person_pii AS
SELECT
  i.submission_id,
  i.first_name, i.last_name,
  i.employee_ssn,
  i.employee_birthday,
  i.employee_gender,
  i.home_address, i.city, i.state, i.zip,
  i.email_address,
  i.cell_phone_number
FROM census_identity i;

-- Elections slice
CREATE VIEW IF NOT EXISTS v_elections AS
SELECT
  i.submission_id,
  i.employee_ssn,
  c.major_medical_coverage, c.medical_effective_date, c.employee_medical_premium,
  c.dental_coverage, c.dental_effective_date, c.employee_dental_premium,
  c.vision_coverage, c.vision_effective_date, c.employee_vision_premium,
  c.group_life_coverage_status, c.group_life_effective_date,
  c.std_coverage, c.std_ltd_effective_date, c.ltd_election
FROM census_identity i
LEFT JOIN census_coverage c ON c.submission_id = i.submission_id;

-- Dependents — UNPIVOT Dep 1-5 into rows
CREATE VIEW IF NOT EXISTS v_dependents AS
SELECT i.submission_id, 1 AS dep_number, d.dep1_action AS action, d.dep1_dep_code AS dep_code, d.dep1_first_name AS first_name, d.dep1_last_name AS last_name, d.dep1_gender AS gender, d.dep1_relationship AS relationship, d.dep1_ssn AS ssn, d.dep1_birthday AS birthday
FROM census_identity i JOIN census_dependents d ON d.submission_id = i.submission_id WHERE d.dep1_first_name IS NOT NULL AND d.dep1_first_name != ''
UNION ALL
SELECT i.submission_id, 2, d.dep2_action, d.dep2_dep_code, d.dep2_first_name, d.dep2_last_name, d.dep2_gender, d.dep2_relationship, d.dep2_ssn, d.dep2_birthday
FROM census_identity i JOIN census_dependents d ON d.submission_id = i.submission_id WHERE d.dep2_first_name IS NOT NULL AND d.dep2_first_name != ''
UNION ALL
SELECT i.submission_id, 3, d.dep3_action, d.dep3_dep_code, d.dep3_first_name, d.dep3_last_name, d.dep3_gender, d.dep3_relationship, d.dep3_ssn, d.dep3_birthday
FROM census_identity i JOIN census_dependents d ON d.submission_id = i.submission_id WHERE d.dep3_first_name IS NOT NULL AND d.dep3_first_name != ''
UNION ALL
SELECT i.submission_id, 4, d.dep4_action, d.dep4_dep_code, d.dep4_first_name, d.dep4_last_name, d.dep4_gender, d.dep4_relationship, d.dep4_ssn, d.dep4_birthday
FROM census_identity i JOIN census_dependents d ON d.submission_id = i.submission_id WHERE d.dep4_first_name IS NOT NULL AND d.dep4_first_name != ''
UNION ALL
SELECT i.submission_id, 5, d.dep5_action, d.dep5_dep_code, d.dep5_first_name, d.dep5_last_name, d.dep5_gender, d.dep5_relationship, d.dep5_ssn, d.dep5_birthday
FROM census_identity i JOIN census_dependents d ON d.submission_id = i.submission_id WHERE d.dep5_first_name IS NOT NULL AND d.dep5_first_name != '';
