// ORBT State Machine — goal lifecycle transitions
// Builder CANNOT certify. Separate auditor_certify function.
import type { OrbtMode } from '../types';

const VALID_TRANSITIONS: Record<OrbtMode, OrbtMode[]> = {
  BUILD: ['OPERATE', 'REPAIR'],
  OPERATE: ['REPAIR'],
  REPAIR: ['BUILD', 'TROUBLESHOOT_TRAIN'],
  TROUBLESHOOT_TRAIN: ['BUILD'],
};

export function canTransition(from: OrbtMode, to: OrbtMode): boolean {
  return VALID_TRANSITIONS[from].includes(to);
}

// Builder calls this when all stations complete — sets awaiting certification, NOT OPERATE
export function builderComplete(): 'awaiting_certification' {
  return 'awaiting_certification';
}

// Only the auditor can call this — different engine than builder
export function auditorCertify(current: OrbtMode): OrbtMode {
  if (current !== 'BUILD') {
    throw new Error(`Cannot certify from ${current} — must be in BUILD`);
  }
  return 'OPERATE';
}

export function onStationFail(current: OrbtMode): OrbtMode {
  return 'REPAIR';
}

export function onMechanicFix(): OrbtMode {
  return 'BUILD';
}

export function onStrike3(): OrbtMode {
  return 'TROUBLESHOOT_TRAIN';
}

export function onADIssued(): OrbtMode {
  return 'BUILD';
}

export function shouldEscalate(fleetStrikeCount: number): boolean {
  return fleetStrikeCount >= 3;
}
