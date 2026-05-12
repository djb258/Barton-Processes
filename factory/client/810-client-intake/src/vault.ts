/**
 * bp.810 — Client Intake: Vault (stub)
 * Single-tier D1 model adopted 2026-05-12.
 * Neon vault path removed — /vault returns 410 Gone.
 * This file retained as stub so the import does not break index.ts.
 */

// No-op — 410 is returned directly in index.ts on POST /vault
export const VAULT_GONE = 410;
