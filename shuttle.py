from __future__ import annotations

import json
import time as time_module
from datetime import datetime, time
from typing import Any, Iterable, Iterator


ALLOWED_STATUSES = {"ON_ROUTE", "STOPPED"}

SHUTTLE_EVENTS: list[dict[str, Any]] = [
    {"Timestamp": "08:00", "Route": "AITU-Campus–Residence", "Bus": "B01", "Passengers": 18, "Speed_kmh": 31, "Status": "ON_ROUTE"},
    {"Timestamp": "08:01", "Route": "AITU-Campus–Residence", "Bus": "B02", "Passengers": 22, "Speed_kmh": 28, "Status": "ON_ROUTE"},
    {"Timestamp": "08:02", "Route": "AITU-Campus–Residence", "Bus": "B01", "Passengers": 21, "Speed_kmh": 29, "Status": "ON_ROUTE"},
    {"Timestamp": "08:03", "Route": "AITU-Campus–Residence", "Bus": "B02", "Passengers": 25, "Speed_kmh": 27, "Status": "ON_ROUTE"},
    {"Timestamp": "08:04", "Route": "AITU-Campus–Residence", "Bus": "B01", "Passengers": 24, "Speed_kmh": 0, "Status": "STOPPED"},
    {"Timestamp": "08:05", "Route": "AITU-Campus–Residence", "Bus": "B02", "Passengers": 26, "Speed_kmh": 30, "Status": "ON_ROUTE"},
    {"Timestamp": "08:06", "Route": "AITU-Campus–Residence", "Bus": "B01", "Passengers": 23, "Speed_kmh": 32, "Status": "ON_ROUTE"},
    {"Timestamp": "08:07", "Route": "AITU-Campus–Residence", "Bus": "B02", "Passengers": 28, "Speed_kmh": 26, "Status": "ON_ROUTE"},
    {"Timestamp": "08:08", "Route": "AITU-Campus–Residence", "Bus": "B01", "Passengers": 27, "Speed_kmh": 25, "Status": "ON_ROUTE"},
    {"Timestamp": "08:09", "Route": "AITU-Campus–Residence", "Bus": "B02", "Passengers": 30, "Speed_kmh": 24, "Status": "ON_ROUTE"},
]


class EventValidationError(ValueError):
    """Raised when one event contains one or more invalid fields."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _parse_timestamp(value: Any) -> time:
    if isinstance(value, time):
        return value
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string in HH:MM format")
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("Timestamp must be a valid time in HH:MM format") from exc


def _parse_passengers(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("Passengers must be a non-negative integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Passengers must be a non-negative integer") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError("Passengers must be a non-negative integer")
    if isinstance(value, str) and str(parsed) != value.strip():
        raise ValueError("Passengers must be a non-negative integer")
    if parsed < 0:
        raise ValueError("Passengers must be a non-negative integer")
    return parsed


def _parse_speed(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("Speed_kmh must be a number from 0 to 120")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Speed_kmh must be a number from 0 to 120") from exc
    if not 0 <= parsed <= 120:
        raise ValueError("Speed_kmh must be between 0 and 120")
    return parsed


def validate_event(event: dict[str, Any]) -> dict[str, Any]:
    """Parse and validate one raw event, returning a normalized record.

    All detected field errors are returned together through
    ``EventValidationError.errors``.
    """

    if not isinstance(event, dict):
        raise EventValidationError(["Event must be a JSON object/dictionary"])

    errors: list[str] = []
    normalized: dict[str, Any] = {}

    required_fields = ("Timestamp", "Route", "Bus", "Passengers", "Speed_kmh", "Status")
    for field in required_fields:
        if field not in event:
            errors.append(f"Missing field: {field}")

    if "Timestamp" in event:
        try:
            normalized["Timestamp"] = _parse_timestamp(event["Timestamp"])
        except ValueError as exc:
            errors.append(str(exc))

    for field in ("Route", "Bus"):
        if field in event:
            value = event[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string")
            else:
                normalized[field] = value.strip()

    if "Passengers" in event:
        try:
            normalized["Passengers"] = _parse_passengers(event["Passengers"])
        except ValueError as exc:
            errors.append(str(exc))

    if "Speed_kmh" in event:
        try:
            normalized["Speed_kmh"] = _parse_speed(event["Speed_kmh"])
        except ValueError as exc:
            errors.append(str(exc))

    if "Status" in event:
        status = event["Status"]
        if not isinstance(status, str) or status not in ALLOWED_STATUSES:
            errors.append("Status must be ON_ROUTE or STOPPED")
        else:
            normalized["Status"] = status

    if errors:
        raise EventValidationError(errors)
    return normalized


def event_stream(
    events: Iterable[dict[str, Any]], delay_seconds: float = 0
) -> Iterator[dict[str, Any]]:
    """Validate and yield chronological events one at a time.

    ``events`` can be any iterable, including an unlimited source. The function
    never converts it to a list. ``delay_seconds`` may be used for a live demo.
    """

    previous_timestamp: time | None = None
    for raw_event in events:
        event = validate_event(raw_event)
        current_timestamp = event["Timestamp"]
        if previous_timestamp is not None and current_timestamp < previous_timestamp:
            raise EventValidationError(["Events must be in chronological order"])
        previous_timestamp = current_timestamp
        if delay_seconds > 0:
            time_module.sleep(delay_seconds)
        yield event


def occupancy_category(passenger_count: int) -> str:
    if passenger_count <= 10:
        return "LOW"
    if passenger_count <= 20:
        return "MEDIUM"
    if passenger_count <= 30:
        return "HIGH"
    return "OVER_CAPACITY"


def event_to_jsonable(event: dict[str, Any]) -> dict[str, Any]:
    """Return a validated event containing only JSON-compatible values."""

    validated = validate_event(event)
    output = validated.copy()
    output["Timestamp"] = validated["Timestamp"].strftime("%H:%M")
    speed = validated["Speed_kmh"]
    output["Speed_kmh"] = int(speed) if speed.is_integer() else speed
    return output


def events_to_json(events: Iterable[dict[str, Any]]) -> str:
    """Convert supplied events to a formatted JSON array."""

    return json.dumps(
        [event_to_jsonable(event) for event in events],
        ensure_ascii=False,
        indent=2,
    )


def process_stream(events: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Yield a small processing result for each event in a validated stream."""

    for event_number, event in enumerate(event_stream(events), start=1):
        yield {
            "event": event_number,
            "passengers": event["Passengers"],
            "speed": event["Speed_kmh"],
            "status": event["Status"],
            "processed": True,
            "reason": "Valid event received in chronological order",
        }


def analyze_events(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Calculate all required statistics in one pass through the stream."""

    total_passengers = 0
    event_count = 0
    stopped_events = 0
    busiest_event: dict[str, Any] | None = None

    for event in event_stream(events):
        event_count += 1
        total_passengers += event["Passengers"]
        if event["Status"] == "STOPPED":
            stopped_events += 1
        if busiest_event is None or event["Passengers"] > busiest_event["Passengers"]:
            busiest_event = event

    if event_count == 0 or busiest_event is None:
        raise ValueError("Cannot analyze an empty event stream")

    return {
        "average_passengers": total_passengers / event_count,
        "maximum_passengers": busiest_event["Passengers"],
        "stopped_events": stopped_events,
        "busiest_minute": busiest_event["Timestamp"].strftime("%H:%M"),
        "busiest_bus": busiest_event["Bus"],
    }
