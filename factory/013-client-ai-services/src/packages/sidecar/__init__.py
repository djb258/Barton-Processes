"""
CTB Metadata
ctb_id: CTB-A71064E2E8FD
ctb_branch: ai
ctb_path: ai/packages/sidecar/__init__.py
ctb_version: 1.0.0
created: 2025-10-23T16:37:00.552187
checksum: 5f4acacc
"""

"""Sidecar package for IMO Creator"""
from .event_emitter import SidecarEventEmitter, get_emitter, emit_event

__version__ = "1.0.0"
__all__ = ["SidecarEventEmitter", "get_emitter", "emit_event"]