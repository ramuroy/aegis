"""Typed identifiers.

Every identifier in AEGIS is a ULID rendered as a 26-character Crockford
base32 string, wrapped in a distinct ``NewType``.

Two decisions worth explaining, because both cost something.

**Why ULID rather than UUIDv4.** Identifiers here are overwhelmingly written in
time order and read in time ranges: telemetry samples, detections, sortie
events. ULIDs are lexicographically sortable by creation time, which means a
B-tree index on the primary key has locality instead of scattering every insert
across the whole index. It also means an operator reading a log can tell at a
glance which of two IDs happened first, which matters more than it sounds like
during incident review.

**Why ``NewType`` rather than plain ``str``.** These identifiers get passed
through long call chains — a detection on the aircraft becomes a trigger on the
edge node becomes a dispatch becomes a sortie becomes an alert in the cloud — and
at every hop there are three or four IDs in scope at once. ``NewType`` costs
nothing at runtime and makes ``dispatch(site_id, drone_id)`` called with the
arguments swapped a type error rather than a 3 a.m. debugging session.

The trade is that constructing one requires an explicit cast. That friction is
deliberate: it marks the boundary where an untrusted string becomes a trusted
identifier, and that is exactly where validation belongs.
"""

from __future__ import annotations

import os
import time
from typing import Final, NewType

__all__ = [
    "AlertId",
    "DetectionId",
    "DispatchId",
    "DroneId",
    "EventId",
    "IncidentId",
    "PrivacyMapId",
    "SensorNodeId",
    "SiteId",
    "SortieId",
    "TrackId",
    "UserId",
    "ZoneId",
    "new_ulid",
    "ulid_timestamp_ms",
]

# --- Identifier types -------------------------------------------------------
# Grouped by the tier that mints them, because that is the useful distinction
# when reasoning about uniqueness guarantees across a partition.

# Cloud-minted: allocated once, globally, at provisioning time.
SiteId = NewType("SiteId", str)
DroneId = NewType("DroneId", str)
SensorNodeId = NewType("SensorNodeId", str)
UserId = NewType("UserId", str)
ZoneId = NewType("ZoneId", str)
PrivacyMapId = NewType("PrivacyMapId", str)

# Edge-minted: allocated on the site node, which may be partitioned from the
# cloud when it does so. ULID randomness is what makes that collision-safe.
DispatchId = NewType("DispatchId", str)
SortieId = NewType("SortieId", str)
IncidentId = NewType("IncidentId", str)
AlertId = NewType("AlertId", str)
EventId = NewType("EventId", str)

# Onboard-minted: high volume, allocated in the perception loop.
DetectionId = NewType("DetectionId", str)
TrackId = NewType("TrackId", str)


# --- ULID -------------------------------------------------------------------
# Crockford base32: excludes I, L, O and U to avoid transcription ambiguity
# (I/1, L/1, O/0) and to avoid accidentally spelling words.
_CROCKFORD: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_TIME_LEN: Final = 10  # 48 bits of milliseconds -> 10 base32 chars
_RAND_LEN: Final = 16  # 80 bits of randomness   -> 16 base32 chars
_ULID_LEN: Final = _TIME_LEN + _RAND_LEN


def _encode(value: int, length: int) -> str:
    """Encode ``value`` as ``length`` Crockford base32 characters, big-endian."""
    out = [""] * length
    for i in range(length - 1, -1, -1):
        out[i] = _CROCKFORD[value & 0x1F]
        value >>= 5
    return "".join(out)


def new_ulid(*, timestamp_ms: int | None = None) -> str:
    """Mint a new ULID.

    ``timestamp_ms`` is injectable so tests can produce deterministic,
    order-controlled identifiers without monkeypatching the clock. Production
    callers should never pass it.

    Randomness comes from ``os.urandom`` rather than the ``random`` module: these
    identifiers appear in URLs and in the audit log, and a predictable sequence
    would let an observer enumerate incidents they were not shown.
    """
    ts = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    if not 0 <= ts < (1 << 48):
        raise ValueError(f"timestamp out of 48-bit ULID range: {ts}")
    rand = int.from_bytes(os.urandom(10), "big")  # 80 bits
    return _encode(ts, _TIME_LEN) + _encode(rand, _RAND_LEN)


def ulid_timestamp_ms(ulid: str) -> int:
    """Recover the creation timestamp from a ULID.

    Useful in exactly one place that matters: reconstructing event ordering
    during incident review when the edge node's wall clock disagreed with the
    cloud's, which happens after a long partition.
    """
    if len(ulid) != _ULID_LEN:
        raise ValueError(f"not a ULID (expected {_ULID_LEN} chars, got {len(ulid)})")
    value = 0
    for ch in ulid[:_TIME_LEN]:
        idx = _CROCKFORD.find(ch.upper())
        if idx < 0:
            raise ValueError(f"invalid Crockford base32 character: {ch!r}")
        value = (value << 5) | idx
    return value
