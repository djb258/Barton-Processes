# Reflect Health Data Dictionary

Source: Reflect Health inbound_template.xlsx — Data Dictionary sheet

| Column ID | Original Label | Snake Name | Category | Classification | Required | Format | Description |
|-----------|---------------|------------|----------|----------------|----------|--------|-------------|
| RH-001 | Employer | employer | employment | Operational |  | text | Employer |
| RH-002 | SubscriberNumber | subscribernumber | identity | PHI | Y | ssn 9-digit | The subscriber number is used to uniquely define an employee.  This is employees 9 digit social security number with or with out dashes. |
| RH-003 | RelationshipCode | relationshipcode | identity | PII | Y | enum:1|2|3|4 | Identifies the relationship of the member to the subscriber.  Use: 1 for a subscriber, 2 for a spouse, 3 for a child, 4 for other |
| RH-004 | MemberLastName | memberlastname | identity | PII | Y | text | Member's Last Name including SR, JR, etc. (without comma) |
| RH-005 | MemberFirstName | memberfirstname | identity | PII | Y | text | Member's formal first name. |
| RH-006 | MemberMiddleInitial | membermiddleinitial | identity | PII |  | text | MemberMiddleInitial |
| RH-007 | AddressLine1 | addressline1 | contact | PII | Y | text | Mailing Address line 1 |
| RH-008 | AddressLine2 | addressline2 | contact | PII |  | text | Mailing additional Address.  space if none. |
| RH-009 | City | city | contact | PII | Y | text | Mailing City |
| RH-010 | State | state | contact | PII | Y | text | Mailing state code. |
| RH-011 | ZipCode | zipcode | contact | PII | Y | text 5-or-9-digit | Mailing zip code. Format as 99999-9999 or 99999) |
| RH-012 | Country | country | contact | PII |  | text | Member's country  Default is USA |
| RH-013 | HomePhone | homephone | contact | PII |  | text | Member's 10 digit home phone number. |
| RH-014 | WorkPhone | workphone | contact | PII |  | text | Member's 10 digit work phone number |
| RH-015 | DateOfBirth | dateofbirth | identity | PHI | Y | date YYYY-MM-DD | Member's Birthday formatted as Any valid date format. |
| RH-016 | EmailAddress | emailaddress | contact | PII |  | text | Member's E-Mail address |
| RH-017 | Gender | gender | identity | PII | Y | enum:M|F|U | The member's gender, use:  F for a Female member, M for a Male member or U |
| RH-018 | SocialSecurityNumber | socialsecuritynumber | identity | PHI | Y | ssn 9-digit | Enter the 9 digit social security number of the member if known.  For the subscriber this should always be the same as the Subscriber Number. |
| RH-019 | HiredDate | hireddate | employment | Operational | Y | date YYYY-MM-DD | HiredDate |
| RH-020 | DateofDeath | dateofdeath | metadata | Operational |  | date YYYY-MM-DD | DateofDeath |
| RH-021 | MemberStatus | memberstatus | identity | PII |  | text | Student or Handicapped Status, use S, H or blank |
| RH-022 | MemberStatusDate | memberstatusdate | identity | PII |  | date YYYY-MM-DD | Date on which Student or Handicapped status was last verified. |
| RH-023 | MaritalStatus | maritalstatus | identity | PII |  | text | Member's Marital Status  S for single, M for married, D for divorced, W for widowed |
| RH-024 | RetiredCode | retiredcode | metadata | Operational |  | text | The member's retired status:  Y for retired, N for not retired |
| RH-025 | SmokerCode | smokercode | identity | PII |  | text | The member's smoker status:  Y for smoker, N for non-smoker |
| RH-026 | VIPCode | vipcode | metadata | Operational |  | text | VIP Member, use Y (yes) or N (no) |
| RH-027 | ClientLevelCode | clientlevelcode | coverage | Operational | Y | text | Assigned by S&S; Please request if not given. |
| RH-028 | GroupNumber | groupnumber | coverage | Operational | Y | text | Parent Group Code as setup with S&S.  Please request if not given. |
| RH-029 | GroupLocationNumber | grouplocationnumber | coverage | Operational | Y | text | Group Location as setup wity S&S.  Please request if not given. |
| RH-030 | CobraCode | cobracode | cobra | PHI |  | text | Cobra Benefits code  C for receiving Cobra, ' ' for not receiving |
| RH-031 | GroupEffectiveDate | groupeffectivedate | coverage | Operational |  | date YYYY-MM-DD | Effective date the member started in the group and location. |
| RH-032 | GroupTerminationDate | groupterminationdate | coverage | Operational |  | date YYYY-MM-DD | Date the member was terminated from coverage or from the group and location in fields 27 & 28.  If still active, please use 99991231 but can be blank. |
| RH-033 | MemberPaidThruDate | memberpaidthrudate | identity | PII |  | date YYYY-MM-DD | Date the member's coverages are paid up to (thru) |
| RH-034 | MedicalCoverageType | medicalcoveragetype | medical | PHI | Y | enum:see_data_dictionary | Level or Plan code for medical coverage. |
| RH-035 | MedicalCoverageTier | medicalcoveragetier | medical | PHI | Y | enum:see_data_dictionary | Tier code for medical coverage |
| RH-036 | MedicalEffectiveDate | medicaleffectivedate | medical | PHI | Y | date YYYY-MM-DD | Effective Date for the specific benefit coverage listed.  If the  information for determining group or benefit level changes, this date MUST reflect the change date of coverage. This date is used in the actual update program. Use Any valid date format. |
| RH-037 | MedicalTerminationDate | medicalterminationdate | medical | PHI | Y | date YYYY-MM-DD | Required if member is terming.  Termination Date for the specific benefit coverage listed. |
| RH-038 | DentalCoverageType | dentalcoveragetype | dental | PHI |  | enum:see_data_dictionary | DentalCoverageType |
| RH-039 | DentalCoverageTier | dentalcoveragetier | dental | PHI |  | enum:see_data_dictionary | DentalCoverageTier |
| RH-040 | DentalEffectiveDate | dentaleffectivedate | dental | PHI |  | date YYYY-MM-DD | DentalEffectiveDate |
| RH-041 | DentalTerminationDate | dentalterminationdate | dental | PHI |  | date YYYY-MM-DD | DentalTerminationDate |
| RH-042 | VisionCoverageType | visioncoveragetype | vision | PHI |  | enum:see_data_dictionary | VisionCoverageType |
| RH-043 | VisionCoverageTier | visioncoveragetier | vision | PHI |  | enum:see_data_dictionary | VisionCoverageTier |
| RH-044 | VisionEffectiveDate | visioneffectivedate | vision | PHI |  | date YYYY-MM-DD | VisionEffectiveDate |
| RH-045 | VisionTerminationDate | visionterminationdate | vision | PHI |  | date YYYY-MM-DD | VisionTerminationDate |
| RH-046 | DisabilityCoverageType | disabilitycoveragetype | coverage | Operational |  | enum:see_data_dictionary | DisabilityCoverageType |
| RH-047 | DisabilityEffectiveDate | disabilityeffectivedate | coverage | Operational |  | date YYYY-MM-DD | DisabilityEffectiveDate |
| RH-048 | DisabilityTerminationDate | disabilityterminationdate | coverage | Operational |  | date YYYY-MM-DD | DisabilityTerminationDate |
| RH-049 | DisabilityCoverageAmount | disabilitycoverageamount | coverage | Operational |  | text | DisabilityCoverageAmount |
| RH-050 | FlexPayrollPeriod | flexpayrollperiod | flex | PHI |  | text | FlexPayrollPeriod |
| RH-051 | FlexCoverageType | flexcoveragetype | flex | PHI |  | enum:see_data_dictionary | FlexCoverageType |
| RH-052 | FlexMedicalPayPeriodCont | flexmedicalpayperiodcont | medical | PHI |  | text | FlexMedicalPayPeriodCont |
| RH-053 | FlexMedicalYearlyTotal | flexmedicalyearlytotal | medical | PHI |  | text | FlexMedicalYearlyTotal |
| RH-054 | FlexEffectiveDate | flexeffectivedate | flex | PHI |  | date YYYY-MM-DD | FlexEffectiveDate |
| RH-055 | FlexTerminationDate | flexterminationdate | flex | PHI |  | date YYYY-MM-DD | FlexTerminationDate |
| RH-056 | FlexDependentPayPeriodCont | flexdependentpayperiodcont | flex | PHI |  | text | FlexDependentPayPeriodCont |
| RH-057 | FlexTransPayPeriodCont | flextranspayperiodcont | flex | PHI |  | text | FlexTransPayPeriodCont |
| RH-058 | LifeCoverageType | lifecoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeCoverageType |
| RH-059 | LifeEffectiveDate | lifeeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeEffectiveDate |
| RH-060 | LifeTerminationDate | lifeterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeTerminationDate |
| RH-061 | LifeCoverageAmount | lifecoverageamount | life_add | PHI |  | text | LifeCoverageAmount |
| RH-062 | ADADCoverageType | adadcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADCoverageType |
| RH-063 | ADADEffectiveDate | adadeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADEffectiveDate |
| RH-064 | ADADTerminationDate | adadterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADTerminationDate |
| RH-065 | ADADCoverageAmount | adadcoverageamount | coverage | Operational |  | text | ADADCoverageAmount |
| RH-066 | HRACoverageType | hracoveragetype | hra | PHI |  | enum:see_data_dictionary | HRACoverageType |
| RH-067 | HRAEffectiveDate | hraeffectivedate | hra | PHI |  | date YYYY-MM-DD | HRAEffectiveDate |
| RH-068 | HRATerminationDate | hraterminationdate | hra | PHI |  | date YYYY-MM-DD | HRATerminationDate |
| RH-069 | PreexistingExpirationDate | preexistingexpirationdate | metadata | Operational |  | date YYYY-MM-DD | PreexistingExpirationDate |
| RH-070 | Network1 | network1 | metadata | Operational |  | text | Network/PPO |
| RH-071 | Network1EffectiveDate | network1effectivedate | coverage | Operational |  | date YYYY-MM-DD | Effective Date for network/PPO |
| RH-072 | Network2 | network2 | metadata | Operational |  | text | Network/PPO |
| RH-073 | Network2EffectiveDate | network2effectivedate | coverage | Operational |  | date YYYY-MM-DD | Effective Date for network/PPO |
| RH-074 | Network3 | network3 | metadata | Operational |  | text | Network/PPO |
| RH-075 | Network3EffectiveDate | network3effectivedate | coverage | Operational |  | date YYYY-MM-DD | Effective Date for network/PPO |
| RH-076 | PrimaryPCPID | primarypcpid | metadata | Operational |  | text | This is the primary PCP's ID or Tax ID  **NOTE:  If PCP changes then current MED plan terminates. |
| RH-077 | PrimaryPCPEffectiveDate | primarypcpeffectivedate | coverage | Operational |  | date YYYY-MM-DD | This is the effective date of the primary PCP and/or primary provider organization.  Use the Any valid date format. |
| RH-078 | PayrollInternalCode | payrollinternalcode | metadata | Operational |  | text | PayrollInternalCode |
| RH-079 | OtherData | otherdata | metadata | Operational |  | text | Additional information that needs to be conveyed |
| RH-080 | OtherData2 | otherdata2 | metadata | Operational |  | text | Additional information that needs to be conveyed. |
| RH-081 | AlternateID | alternateid | metadata | Operational |  | text | Unique (per person) alternate id to be used for identification |
| RH-082 | Rider01 | rider01 | rider | PHI |  | text | Rider01 |
| RH-083 | Rider02 | rider02 | rider | PHI |  | text | Rider02 |
| RH-084 | Rider03 | rider03 | rider | PHI |  | text | Rider03 |
| RH-085 | Rider04 | rider04 | rider | PHI |  | text | Rider04 |
| RH-086 | Rider05 | rider05 | rider | PHI |  | text | Rider05 |
| RH-087 | Rider06 | rider06 | rider | PHI |  | text | Rider06 |
| RH-088 | Rider07 | rider07 | rider | PHI |  | text | Rider07 |
| RH-089 | Rider08 | rider08 | rider | PHI |  | text | Rider08 |
| RH-090 | Rider09 | rider09 | rider | PHI |  | text | Rider09 |
| RH-091 | Rider10 | rider10 | rider | PHI |  | text | Rider10 |
| RH-092 | MedicalTermReason | medicaltermreason | medical | PHI |  | text | Medical Termination of Coverage Reason. |
| RH-093 | DentalTermReason | dentaltermreason | dental | PHI |  | text | Termination of Coverage Reason. |
| RH-094 | VisionTermReason | visiontermreason | vision | PHI |  | text | Termination of Coverage Reason. |
| RH-095 | DisabilityTermReason | disabilitytermreason | coverage | Operational |  | text | DisabilityTermReason |
| RH-096 | FlexTermReason | flextermreason | flex | PHI |  | text | FlexTermReason |
| RH-097 | LifeTermReason | lifetermreason | life_add | PHI |  | text | LifeTermReason |
| RH-098 | ADADTermReason | adadtermreason | coverage | Operational |  | text | ADADTermReason |
| RH-099 | HRATermReason | hratermreason | hra | PHI |  | text | HRATermReason |
| RH-100 | HSATermReason | hsatermreason | hsa | PHI |  | text | HSATermReason |
| RH-101 | LTDTermReason | ltdtermreason | std_ltd | PHI |  | text | LTDTermReason |
| RH-102 | LifeSpTermReason | lifesptermreason | life_add | PHI |  | text | LifeSpTermReason |
| RH-103 | LifeDpTermReason | lifedptermreason | life_add | PHI |  | text | LifeDpTermReason |
| RH-104 | LifeSupTermReason | lifesuptermreason | life_add | PHI |  | text | LifeSupTermReason |
| RH-105 | LifeSupSpTermReason | lifesupsptermreason | life_add | PHI |  | text | LifeSupSpTermReason |
| RH-106 | LifeSupDpTermReason | lifesupdptermreason | life_add | PHI |  | text | LifeSupDpTermReason |
| RH-107 | ADADSpTermReason | adadsptermreason | coverage | Operational |  | text | ADADSpTermReason |
| RH-108 | ADADDpTermReason | adaddptermreason | coverage | Operational |  | text | ADADDpTermReason |
| RH-109 | ADADSupTermReason | adadsuptermreason | coverage | Operational |  | text | ADADSupTermReason |
| RH-110 | ADADSupSpTermReason | adadsupsptermreason | coverage | Operational |  | text | ADADSupSpTermReason |
| RH-111 | ADADSupDpTermReason | adadsupdptermreason | coverage | Operational |  | text | ADADSupDpTermReason |
| RH-112 | HSACoverageType | hsacoveragetype | hsa | PHI |  | enum:see_data_dictionary | HSACoverageType |
| RH-113 | HSAEffectiveDate | hsaeffectivedate | hsa | PHI |  | date YYYY-MM-DD | HSAEffectiveDate |
| RH-114 | HSATerminationDate | hsaterminationdate | hsa | PHI |  | date YYYY-MM-DD | HSATerminationDate |
| RH-115 | LTDCoverageType | ltdcoveragetype | std_ltd | PHI |  | enum:see_data_dictionary | LTDCoverageType |
| RH-116 | LTDEffectiveDate | ltdeffectivedate | std_ltd | PHI |  | date YYYY-MM-DD | LTDEffectiveDate |
| RH-117 | LTDTerminationDate | ltdterminationdate | std_ltd | PHI |  | date YYYY-MM-DD | LTDTerminationDate |
| RH-118 | LTDCoverageAmount | ltdcoverageamount | std_ltd | PHI |  | text | LTDCoverageAmount |
| RH-119 | LifeSpCoverageType | lifespcoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeSpCoverageType |
| RH-120 | LifeSpEffectiveDate | lifespeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeSpEffectiveDate |
| RH-121 | LifeSpTerminationDate | lifespterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeSpTerminationDate |
| RH-122 | LifeSpCoverageAmount | lifespcoverageamount | life_add | PHI |  | text | LifeSpCoverageAmount |
| RH-123 | LifeDpCoverageType | lifedpcoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeDpCoverageType |
| RH-124 | LifeDpEffectiveDate | lifedpeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeDpEffectiveDate |
| RH-125 | LifeDpTerminationDate | lifedpterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeDpTerminationDate |
| RH-126 | LifeDpCoverageAmount | lifedpcoverageamount | life_add | PHI |  | text | LifeDpCoverageAmount |
| RH-127 | LifeSupCoverageType | lifesupcoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeSupCoverageType |
| RH-128 | LifeSupEffectiveDate | lifesupeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeSupEffectiveDate |
| RH-129 | LifeSupTerminationDate | lifesupterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeSupTerminationDate |
| RH-130 | LifeSupCoverageAmount | lifesupcoverageamount | life_add | PHI |  | text | LifeSupCoverageAmount |
| RH-131 | LifeSupSpCoverageType | lifesupspcoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeSupSpCoverageType |
| RH-132 | LifeSupSpEffectiveDate | lifesupspeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeSupSpEffectiveDate |
| RH-133 | LifeSupSpTerminationDate | lifesupspterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeSupSpTerminationDate |
| RH-134 | LifeSupSpCoverageAmount | lifesupspcoverageamount | life_add | PHI |  | text | LifeSupSpCoverageAmount |
| RH-135 | LifeSupDpCoverageType | lifesupdpcoveragetype | life_add | PHI |  | enum:see_data_dictionary | LifeSupDpCoverageType |
| RH-136 | LifeSupDpEffectiveDate | lifesupdpeffectivedate | life_add | PHI |  | date YYYY-MM-DD | LifeSupDpEffectiveDate |
| RH-137 | LifeSupDpTerminationDate | lifesupdpterminationdate | life_add | PHI |  | date YYYY-MM-DD | LifeSupDpTerminationDate |
| RH-138 | LifeSupDpCoverageAmount | lifesupdpcoverageamount | life_add | PHI |  | text | LifeSupDpCoverageAmount |
| RH-139 | ADADSpCoverageType | adadspcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADSpCoverageType |
| RH-140 | ADADSpEffectiveDate | adadspeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADSpEffectiveDate |
| RH-141 | ADADSpTerminationDate | adadspterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADSpTerminationDate |
| RH-142 | ADADSpCoverageAmount | adadspcoverageamount | coverage | Operational |  | text | ADADSpCoverageAmount |
| RH-143 | ADADDpCoverageType | adaddpcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADDpCoverageType |
| RH-144 | ADADDpEffectiveDate | adaddpeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADDpEffectiveDate |
| RH-145 | ADADDpTerminationDate | adaddpterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADDpTerminationDate |
| RH-146 | ADADDpCoverageAmount | adaddpcoverageamount | coverage | Operational |  | text | ADADDpCoverageAmount |
| RH-147 | ADADSupCoverageType | adadsupcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADSupCoverageType |
| RH-148 | ADADSupEffectiveDate | adadsupeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADSupEffectiveDate |
| RH-149 | ADADSupTerminationDate | adadsupterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADSupTerminationDate |
| RH-150 | ADADSupCoverageAmount | adadsupcoverageamount | coverage | Operational |  | text | ADADSupCoverageAmount |
| RH-151 | ADADSupSpCoverageType | adadsupspcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADSupSpCoverageType |
| RH-152 | ADADSupSpEffectiveDate | adadsupspeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADSupSpEffectiveDate |
| RH-153 | ADADSupSpTerminationDate | adadsupspterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADSupSpTerminationDate |
| RH-154 | ADADSupSpCoverageAmount | adadsupspcoverageamount | coverage | Operational |  | text | ADADSupSpCoverageAmount |
| RH-155 | ADADSupDpCoverageType | adadsupdpcoveragetype | coverage | Operational |  | enum:see_data_dictionary | ADADSupDpCoverageType |
| RH-156 | ADADSupDpEffectiveDate | adadsupdpeffectivedate | coverage | Operational |  | date YYYY-MM-DD | ADADSupDpEffectiveDate |
| RH-157 | ADADSupDpTerminationDate | adadsupdpterminationdate | coverage | Operational |  | date YYYY-MM-DD | ADADSupDpTerminationDate |
| RH-158 | ADADSupDpCoverageAmount | adadsupdpcoverageamount | coverage | Operational |  | text | ADADSupDpCoverageAmount |
| RH-159 | STDSupCoverageType | stdsupcoveragetype | std_ltd | PHI |  | enum:see_data_dictionary | STDSupCoverageType |
| RH-160 | STDSupEffectiveDate | stdsupeffectivedate | std_ltd | PHI |  | date YYYY-MM-DD | STDSupEffectiveDate |
| RH-161 | STDSupTerminationDate | stdsupterminationdate | std_ltd | PHI |  | date YYYY-MM-DD | STDSupTerminationDate |
| RH-162 | STDSupCoverageAmount | stdsupcoverageamount | std_ltd | PHI |  | text | STDSupCoverageAmount |
| RH-163 | LTDSupCoverageType | ltdsupcoveragetype | std_ltd | PHI |  | enum:see_data_dictionary | LTDSupCoverageType |
| RH-164 | LTDSupEffectiveDate | ltdsupeffectivedate | std_ltd | PHI |  | date YYYY-MM-DD | LTDSupEffectiveDate |
| RH-165 | LTDSupTerminationDate | ltdsupterminationdate | std_ltd | PHI |  | date YYYY-MM-DD | LTDSupTerminationDate |
| RH-166 | LTDSupCoverageAmount | ltdsupcoverageamount | std_ltd | PHI |  | text | LTDSupCoverageAmount |
| RH-167 | STDSupTermReason | stdsuptermreason | std_ltd | PHI |  | text | STDSupTermReason |
| RH-168 | LTDSupTermReason | ltdsuptermreason | std_ltd | PHI |  | text | LTDSupTermReason |
| RH-169 | CRICoverageType | cricoveragetype | coverage | Operational |  | enum:see_data_dictionary | CRICoverageType |
| RH-170 | CRICoverageTier | cricoveragetier | coverage | Operational |  | enum:see_data_dictionary | CRICoverageTier |
| RH-171 | CRIEffectiveDate | crieffectivedate | coverage | Operational |  | date YYYY-MM-DD | CRIEffectiveDate |
| RH-172 | CRITerminationDate | criterminationdate | coverage | Operational |  | date YYYY-MM-DD | CRITerminationDate |
| RH-173 | CRITermReason | critermreason | coverage | Operational |  | text | CRITermReason |
| RH-174 | IDMCoverageType | idmcoveragetype | flex | PHI |  | enum:see_data_dictionary | IDMCoverageType |
| RH-175 | IDMCoverageTier | idmcoveragetier | flex | PHI |  | enum:see_data_dictionary | IDMCoverageTier |
| RH-176 | IDMEffectiveDate | idmeffectivedate | flex | PHI |  | date YYYY-MM-DD | IDMEffectiveDate |
| RH-177 | IDMTerminationDate | idmterminationdate | flex | PHI |  | date YYYY-MM-DD | IDMTerminationDate |
| RH-178 | IDMTermReason | idmtermreason | flex | PHI |  | text | IDMTermReason |
| RH-179 | RXPCoverageType | rxpcoveragetype | rx | PHI |  | enum:see_data_dictionary | RXPCoverageType |
| RH-180 | RXPCoverageTier | rxpcoveragetier | rx | PHI |  | enum:see_data_dictionary | RXPCoverageTier |
| RH-181 | RXPEffectiveDate | rxpeffectivedate | rx | PHI |  | date YYYY-MM-DD | RXPEffectiveDate |
| RH-182 | RXPTerminationDate | rxpterminationdate | rx | PHI |  | date YYYY-MM-DD | RXPTerminationDate |
| RH-183 | RXPTermReason | rxptermreason | rx | PHI |  | text | RXPTermReason |