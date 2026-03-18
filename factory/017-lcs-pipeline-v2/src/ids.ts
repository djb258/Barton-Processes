// ═══════════════════════════════════════════════════════════════
// ID Minting — BAR-152 Numbering Schema
// ═══════════════════════════════════════════════════════════════
// Authority: Tier 0 §CTB — IDs propagate from leaf to trunk
// Chain: signal → CID → SID → MID (bidirectional)
// ═══════════════════════════════════════════════════════════════

import type { LifecyclePhase, Channel } from './types';

function ulid(): string {
  const ts = Date.now().toString(36).padStart(10, '0');
  const rand = Array.from({ length: 16 }, () =>
    Math.floor(Math.random() * 36).toString(36)
  ).join('');
  return (ts + rand).toUpperCase();
}

function dateStamp(): string {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '');
}

/**
 * Mint a Communication ID (CID)
 * Format: CID-{PHASE}-{DATE}-{ULID}
 * Minted at: Phase 1 (CID Compiler)
 */
export function mintCommunicationId(phase: LifecyclePhase): string {
  return `CID-${phase}-${dateStamp()}-${ulid()}`;
}

/**
 * Mint a Signal Intelligence Document ID (SID)
 * Format: SID-{DATE}-{ULID}
 * Minted at: Phase 3 (SID Constructor)
 */
export function mintSidId(): string {
  return `SID-${dateStamp()}-${ulid()}`;
}

/**
 * Mint a Marketing Intelligence Document ID (MID)
 * Format: MID-{COMM_ID}-{CHANNEL}-{ATTEMPT}
 * Minted at: Phase 4 (MID Engine)
 */
export function mintMessageRunId(
  communicationId: string,
  channel: Channel,
  attempt: number
): string {
  return `MID-${communicationId}-${channel}-${attempt}`;
}
