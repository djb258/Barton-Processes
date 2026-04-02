// ═══════════════════════════════════════════════════════════════
// Line Definitions — Dependency graphs from EXECUTION_ORDER.md
// ═══════════════════════════════════════════════════════════════
// Source of truth: Barton-Processes/EXECUTION_ORDER.md
// Children conform to parent. These are READ from doctrine, not hand-typed.

import type { LineDef } from './types';

export const LINES: Record<string, LineDef> = {
  outreach: {
    name: 'Outreach Line',
    silo: 'svg-agency',
    description: 'Full enrichment pipeline — seed through campaign delivery',
    phases: ['seed', 'enrichment', 'compile'],
    stations: [
      { id: '010-seed', name: 'SVG D1 SEED', process_id: 'PROC-010', phase: 'seed', depends_on: [], adapter_type: 'http', adapter_target: 'https://lcs-hub.svg-outreach.workers.dev', endpoint: '/seed', runtime: 'CF Worker', orbt: 'OPERATE' },
      { id: '300-recon', name: 'Company Reconnaissance', process_id: 'PROC-300', phase: 'enrichment', depends_on: ['010-seed'], adapter_type: 'cli', adapter_target: 'python3 factory/outreach/300-blog-worker/src/company-recon.py', runtime: 'Python script', orbt: 'OPERATE' },
      { id: '400-dol', name: 'DOL Views', process_id: 'PROC-400', phase: 'enrichment', depends_on: ['010-seed'], adapter_type: 'sql', adapter_target: "SELECT * FROM v_dol_renewal_window WHERE company_id = ?", runtime: 'SQL views', orbt: 'OPERATE' },
      { id: '200-people', name: 'Find Person', process_id: 'PROC-200', phase: 'enrichment', depends_on: ['300-recon'], adapter_type: 'cli', adapter_target: 'python3 factory/outreach/200-people-worker/src/find-person-v3.py', runtime: 'Python script', orbt: 'BUILD' },
      { id: '201-email', name: 'Find Email', process_id: 'PROC-201', phase: 'enrichment', depends_on: ['200-people'], adapter_type: 'cli', adapter_target: 'python3 factory/outreach/201-email-discovery/src/find-email.py', runtime: 'Python script', orbt: 'BUILD', conditional: true, condition: 'Only for slots with name but no email' },
      { id: '202-linkedin', name: 'Find LinkedIn', process_id: 'PROC-202', phase: 'enrichment', depends_on: ['200-people'], adapter_type: 'cli', adapter_target: 'python3 factory/outreach/202-linkedin-discovery/src/find-linkedin.py', runtime: 'Python script', orbt: 'BUILD', conditional: true, condition: 'Only for slots with name but no LinkedIn' },
      { id: '500-talent', name: 'Talent Flow', process_id: 'PROC-500', phase: 'enrichment', depends_on: ['200-people'], adapter_type: 'cli', adapter_target: 'python3 factory/outreach/500-talent-flow/src/talent-flow.py', runtime: 'Python script', orbt: 'BUILD' },
      { id: '100-lcs', name: 'LCS Pipeline', process_id: 'PROC-100', phase: 'compile', depends_on: ['200-people', '201-email', '202-linkedin', '400-dol', '500-talent'], adapter_type: 'http', adapter_target: 'https://lcs-hub.svg-outreach.workers.dev', endpoint: '/compile', runtime: 'CF Worker', orbt: 'OPERATE' },
      { id: '700-campaign', name: 'Campaign Engine', process_id: 'PROC-700', phase: 'compile', depends_on: ['100-lcs'], adapter_type: 'http', adapter_target: 'https://lcs-hub.svg-outreach.workers.dev', endpoint: '/campaign', runtime: 'CF Worker', orbt: 'BUILD' },
    ],
  },

  conversion: {
    name: 'Conversion Line',
    silo: 'svg-agency',
    description: 'Prospect response through client onboarding',
    phases: ['sales', 'onboarding'],
    stations: [
      { id: '900-sales', name: 'Sales Portal', process_id: 'PROC-900', phase: 'sales', depends_on: [], adapter_type: 'manual', adapter_target: 'not-built', runtime: 'Not built', orbt: 'BUILD' },
      { id: '800-mint', name: 'Client Mint', process_id: 'PROC-800', phase: 'onboarding', depends_on: ['900-sales'], adapter_type: 'manual', adapter_target: 'not-built', runtime: 'Not built', orbt: 'BUILD' },
      { id: '810-intake', name: 'Client Intake', process_id: 'PROC-810', phase: 'onboarding', depends_on: ['800-mint'], adapter_type: 'manual', adapter_target: 'not-built', runtime: 'Not built', orbt: 'BUILD' },
      { id: '820-export', name: 'Vendor Export', process_id: 'PROC-820', phase: 'onboarding', depends_on: ['810-intake'], adapter_type: 'manual', adapter_target: 'not-built', runtime: 'Not built', orbt: 'BUILD' },
      { id: '830-portal', name: 'Client Portal', process_id: 'PROC-830', phase: 'onboarding', depends_on: ['810-intake'], adapter_type: 'manual', adapter_target: 'not-built', runtime: 'Not built', orbt: 'BUILD' },
    ],
  },

  cl: {
    name: 'Company Lifecycle Line',
    silo: 'svg-agency',
    description: 'LCS compilation',
    phases: ['compile'],
    stations: [
      { id: '100-lcs', name: 'LCS Pipeline', process_id: 'PROC-100', phase: 'compile', depends_on: [], adapter_type: 'http', adapter_target: 'https://lcs-hub.svg-outreach.workers.dev', endpoint: '/compile', runtime: 'CF Worker', orbt: 'OPERATE' },
    ],
  },

  imo: {
    name: 'IMO-Creator Line',
    silo: 'imo-creator',
    description: 'Internal tooling',
    phases: ['internal'],
    stations: [
      { id: '000-adapter', name: 'Adapter Build', process_id: 'PROC-000', phase: 'internal', depends_on: [], adapter_type: 'manual', adapter_target: 'manual', runtime: 'Claude Code', orbt: 'OPERATE' },
      { id: '050-lbb', name: 'LBB Operations', process_id: 'PROC-050', phase: 'internal', depends_on: [], adapter_type: 'http', adapter_target: 'https://lbb.svg-outreach.workers.dev', endpoint: '/ingest', runtime: 'CF Worker', orbt: 'OPERATE' },
    ],
  },
};

export function getLine(name: string): LineDef | undefined {
  return LINES[name];
}

export function getAllLines(): string[] {
  return Object.keys(LINES);
}
