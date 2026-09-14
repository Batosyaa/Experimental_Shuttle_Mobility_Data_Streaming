"""Unit tests for validation, streaming, categorization, and analysis."""

import unittest

from shuttle import (
    EventValidationError,
    SHUTTLE_EVENTS,
    analyze_events,
    event_stream,
    occupancy_category,
    validate_event,
)


class ShuttleTests(unittest.TestCase):
    def test_valid_event_is_parsed(self) -> None:
        event = validate_event(SHUTTLE_EVENTS[0])
        self.assertEqual(event["Timestamp"].strftime("%H:%M"), "08:00")
        self.assertEqual(event["Passengers"], 18)
        self.assertEqual(event["Speed_kmh"], 31.0)

    def test_negative_passengers_are_rejected(self) -> None:
        event = SHUTTLE_EVENTS[0] | {"Passengers": -1}
        with self.assertRaises(EventValidationError) as context:
            validate_event(event)
        self.assertIn("Passengers must be a non-negative integer", context.exception.errors)

    def test_speed_above_120_is_rejected(self) -> None:
        event = SHUTTLE_EVENTS[0] | {"Speed_kmh": 121}
        with self.assertRaises(EventValidationError):
            validate_event(event)

    def test_invalid_status_is_rejected(self) -> None:
        event = SHUTTLE_EVENTS[0] | {"Status": "DELAYED"}
        with self.assertRaises(EventValidationError):
            validate_event(event)

    def test_occupancy_boundaries(self) -> None:
        self.assertEqual(occupancy_category(10), "LOW")
        self.assertEqual(occupancy_category(11), "MEDIUM")
        self.assertEqual(occupancy_category(21), "HIGH")
        self.assertEqual(occupancy_category(31), "OVER_CAPACITY")

    def test_out_of_order_stream_is_rejected(self) -> None:
        events = [SHUTTLE_EVENTS[1], SHUTTLE_EVENTS[0]]
        with self.assertRaises(EventValidationError):
            list(event_stream(events))

    def test_required_analysis_results(self) -> None:
        result = analyze_events(SHUTTLE_EVENTS)
        self.assertEqual(result["average_passengers"], 24.4)
        self.assertEqual(result["maximum_passengers"], 30)
        self.assertEqual(result["stopped_events"], 1)
        self.assertEqual(result["busiest_minute"], "08:09")
        self.assertEqual(result["busiest_bus"], "B02")


if __name__ == "__main__":
    unittest.main(verbosity=2)
