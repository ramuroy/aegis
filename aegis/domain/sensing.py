"""The always-on sensing layer: nodes, events, and what makes two of them independent.

Under [ADR-0002](../../docs/adr/0002-trigger-driven-response-not-scheduled-patrol.md)
the drone is a response asset, not a patroller. Fixed cameras and an ESP32
perimeter grid do the continuous sensing, and the aircraft launches only when
those sensors *corroborate* each other.

That makes "independent" a load-bearing word, and it is subtler than it looks.
Two PIR sensors on the same wall agreeing that something moved is not
corroboration — it is one observation counted twice, and in an Indian society
the thing that moved is usually a cat, a monkey, or a branch. Corroboration
requires sensors whose **failure modes do not correlate**.

So events carry a ``SensorClass``, and the classes are grouped into
``ModalityFamily``. Agreement only counts across families. A fence vibration
plus a camera detection is corroboration; two fence sensors is not, no matter
how far apart they are.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aegis.domain.geo import GeoPoint
from aegis.domain.ids import EventId, SensorNodeId, SiteId, ZoneId

__all__ = [
    "ModalityFamily",
    "SensorClass",
    "SensorEvent",
    "SensorHealth",
    "SensorNode",
]


class ModalityFamily(str, Enum):
    """The physical principle a sensor relies on.

    Corroboration counts across families, never within one. This is the whole
    reason the enum exists: it encodes which failure modes are correlated.
    A monkey on the boundary wall trips every ``MECHANICAL`` sensor it touches
    and every ``PASSIVE_IR`` sensor it passes, but it will not simultaneously
    produce a ``VISION`` person-class detection — so requiring two families
    filters exactly the nuisance events that a count-based threshold does not.
    """

    MECHANICAL = "mechanical"
    """Physical disturbance: fence vibration, gate contact, tamper switch."""

    PASSIVE_IR = "passive_ir"
    """Thermal motion: PIR occupancy sensors."""

    BEAM = "beam"
    """Interruption of an active emitted beam: IR barriers, laser tripwires."""

    VISION = "vision"
    """Image-derived: fixed camera or drone detector output."""

    ACOUSTIC = "acoustic"
    """Sound-derived: glass break, raised voices."""

    RF = "rf"
    """Radio-derived: unexpected device presence, gate-fob anomalies."""


class SensorClass(str, Enum):
    """A specific sensor type. Maps many-to-one onto ``ModalityFamily``."""

    FENCE_VIBRATION = "fence_vibration"
    GATE_CONTACT = "gate_contact"
    TAMPER_SWITCH = "tamper_switch"
    PIR_MOTION = "pir_motion"
    IR_BEAM_BREAK = "ir_beam_break"
    FIXED_CAMERA_PERSON = "fixed_camera_person"
    FIXED_CAMERA_VEHICLE = "fixed_camera_vehicle"
    DRONE_VISION_PERSON = "drone_vision_person"
    DRONE_VISION_VEHICLE = "drone_vision_vehicle"
    GLASS_BREAK = "glass_break"
    RF_ANOMALY = "rf_anomaly"

    @property
    def family(self) -> ModalityFamily:
        return _FAMILY[self]


_FAMILY: dict[SensorClass, ModalityFamily] = {
    SensorClass.FENCE_VIBRATION: ModalityFamily.MECHANICAL,
    SensorClass.GATE_CONTACT: ModalityFamily.MECHANICAL,
    SensorClass.TAMPER_SWITCH: ModalityFamily.MECHANICAL,
    SensorClass.PIR_MOTION: ModalityFamily.PASSIVE_IR,
    SensorClass.IR_BEAM_BREAK: ModalityFamily.BEAM,
    SensorClass.FIXED_CAMERA_PERSON: ModalityFamily.VISION,
    SensorClass.FIXED_CAMERA_VEHICLE: ModalityFamily.VISION,
    SensorClass.DRONE_VISION_PERSON: ModalityFamily.VISION,
    SensorClass.DRONE_VISION_VEHICLE: ModalityFamily.VISION,
    SensorClass.GLASS_BREAK: ModalityFamily.ACOUSTIC,
    SensorClass.RF_ANOMALY: ModalityFamily.RF,
}

# Fail loudly at import time if a class is ever added without a family, rather
# than at 2am when it silently fails to corroborate anything.
assert set(_FAMILY) == set(SensorClass), (
    f"SensorClass without a ModalityFamily: {set(SensorClass) - set(_FAMILY)}"
)


class SensorHealth(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    """Reporting, but something is wrong — low battery, high noise floor,
    intermittent link. Events still count, at reduced confidence."""

    STALE = "stale"
    """Has not reported within its expected interval. Events do not count."""

    TAMPERED = "tampered"
    """Tamper switch tripped or housing opened. Events do not count for
    corroboration, but the tamper itself is a high-severity event."""


@dataclass(frozen=True, slots=True)
class SensorNode:
    """A deployed sensor, typically an ESP32 board with one or more transducers."""

    id: SensorNodeId
    site_id: SiteId
    location: GeoPoint
    classes: frozenset[SensorClass]
    zone_id: ZoneId | None = None
    health: SensorHealth = SensorHealth.OK
    heartbeat_interval_s: float = 30.0
    clock_skew_s: float = 0.0
    """Measured offset of this node's clock from site time.

    ESP32 nodes without an RTC drift by seconds per day and reboot with no
    notion of wall time at all. The edge node measures skew from heartbeats and
    stores it here so event timestamps can be corrected before correlation —
    otherwise a node that is 8 seconds fast never corroborates with anything,
    and the failure is silent.
    """

    @property
    def counts_for_corroboration(self) -> bool:
        return self.health in (SensorHealth.OK, SensorHealth.DEGRADED)


@dataclass(frozen=True, slots=True)
class SensorEvent:
    """One observation from one sensor at one moment."""

    id: EventId
    node_id: SensorNodeId
    sensor_class: SensorClass
    at_s: float
    """Site-corrected event time, in seconds. Already adjusted for node clock
    skew — correlation must never see a raw node timestamp."""

    location: GeoPoint
    confidence: float
    zone_id: ZoneId | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    @property
    def family(self) -> ModalityFamily:
        return self.sensor_class.family
