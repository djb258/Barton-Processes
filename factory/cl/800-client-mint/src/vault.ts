/**
 * 800 — Client Mint: Vault promotion — DISABLED
 *
 * Single-tier model adopted 2026-05-12 per Dave.
 * svg-d1-client.clients is canonical. No Neon clnt.* vault tier.
 * vaultClients() is a no-op stub — returns disabled signal.
 * DO NOT re-enable without sovereign sign-off.
 */

export interface VaultResult {
  disabled: boolean;
  reason: string;
}

export async function vaultClients(): Promise<VaultResult> {
  return {
    disabled: true,
    reason: 'Single-tier model (2026-05-12) — svg-d1-client.clients is canonical. No Neon vault promotion tier. This function is a no-op stub.',
  };
}
