# Assignment 1 — Python Fundamentals for Data Streaming

This project processes the synthetic AITU campus shuttle event stream. It uses
plain Python generators and a small FastAPI endpoint so the solution stays easy
to understand and demonstrate.

## Files

- `shuttle.py` — dataset, validation, generator, JSON conversion, and analysis.
- `app.py` — FastAPI `POST /events` endpoint.
- `main.py` — short streaming and analysis demonstration.
- `test_shuttle.py` — seven unit tests.
- `sample_events.json` — supplied dataset in JSON format.
- `TECHNICAL_REPORT.md` — completed report and tables.
- `EXECUTION_EVIDENCE.txt` — captured test, demo, and API results.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install the API dependencies:

```bash
pip install -r requirements.txt
```

## Run the demonstration

```bash
python main.py
```

Expected analysis:

```text
average_passengers: 24.4
maximum_passengers: 30
stopped_events: 1
busiest_minute: 08:09
busiest_bus: B02
```

## Run the tests

```bash
python -m unittest -v
```

## Run the API

```bash
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger page.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{"Timestamp":"08:10","Route":"AITU-Campus–Residence","Bus":"B01","Passengers":31,"Speed_kmh":20,"Status":"ON_ROUTE"}'
```

Expected response:

```json
{
  "accepted": true,
  "errors": [],
  "occupancy_category": "OVER_CAPACITY"
}
```

Rejected example:

```json
{
  "accepted": false,
  "errors": ["Passengers must be a non-negative integer"],
  "occupancy_category": null
}
```

## Oral defense outline

1. Show `SHUTTLE_EVENTS` and `validate_event()` in `shuttle.py`.
2. Explain that `event_stream()` contains `yield` and reads one input at a time.
3. Run `python main.py` and explain the five analysis values.
4. Run `python -m unittest -v` and briefly change one test input.
5. Run the API, open `/docs`, submit one valid and one invalid event.
