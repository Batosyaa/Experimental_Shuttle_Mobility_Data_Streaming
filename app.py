"""FastAPI endpoint for one campus shuttle event."""

from typing import Any

from fastapi import FastAPI

from shuttle import EventValidationError, occupancy_category, validate_event


app = FastAPI(
    title="AITU Campus Shuttle API",
    description="A simple endpoint for Assignment 1.",
    version="1.0.0",
)


@app.post("/events")
def receive_event(event: dict[str, Any]) -> dict[str, Any]:
    """Validate one event and return its acceptance and occupancy result."""

    try:
        validated = validate_event(event)
    except EventValidationError as exc:
        return {
            "accepted": False,
            "errors": exc.errors,
            "occupancy_category": None,
        }

    return {
        "accepted": True,
        "errors": [],
        "occupancy_category": occupancy_category(validated["Passengers"]),
    }
