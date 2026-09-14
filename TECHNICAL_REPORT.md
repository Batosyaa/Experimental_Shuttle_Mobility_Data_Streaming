# Student Technical Report / Submission Record

## Assignment 1 — Python Fundamentals for Data Streaming

### 1. Student and submission information

| Required field | Student entry |
|---|---|
| Student full name | Sbashev Batyrsayan |
| Student ID | 242530 |
| Group / cohort | BDA-2407 |
| Instructor | Serek Azamat |
| Submission date | 14 September 2026 |
| Python version | Python 3.10+ |

### 2. Work record

| Item | Student entry |
|---|---|
| Work start date | 12 September 2026 |
| Work completion date | 14 September 2026 |
| Main tools / libraries used | Python standard library, FastAPI, Uvicorn |
| Source-code file names | `shuttle.py`, `app.py`, `main.py` |
| Test file / notebook name | `test_shuttle.py` |
| README location | `README.md` |

## 3. Implementation report

### 3.1 Data structures and parsing

| Required evidence | Student response / reference |
|---|---|
| Explanation | The supplied dataset is represented as a list of dictionaries named `SHUTTLE_EVENTS`. Each dictionary represents one event. `validate_event()` converts `Timestamp` to `datetime.time`, `Passengers` to `int`, and `Speed_kmh` to `float`. Text fields remain strings. |
| Code / file / function reference | `shuttle.py`: `SHUTTLE_EVENTS`, `_parse_timestamp()`, `_parse_passengers()`, `_parse_speed()`, `validate_event()` |
| Execution evidence / result | The valid-event unit test confirms `"08:00"`, `18`, and `31` are parsed as `time`, `int`, and `float` values. |
| Student-specific observation or decision | I used a list of dictionaries because it directly matches JSON input and is simpler than adding Pandas for only ten records. |

Completed validation table:

| Field | Python type after parsing | Validation rule | Valid example |
|---|---|---|---|
| Timestamp | `datetime.time` | Valid 24-hour `HH:MM` value | `08:04` |
| Passengers | `int` | Non-negative integer | `24` |
| Speed_kmh | `float` | Number from 0 to 120 inclusive | `31` |
| Status | `str` | Exactly `ON_ROUTE` or `STOPPED` | `STOPPED` |

### 3.2 Event validation

| Required evidence | Student response / reference |
|---|---|
| Explanation | `validate_event()` checks all six required fields. It reports all detected validation messages through `EventValidationError.errors`, rather than hiding later errors after the first failure. Route and bus must also be non-empty strings. |
| Code / file / function reference | `shuttle.py`: `EventValidationError` and `validate_event()` |
| Execution evidence / result | `Passengers = -1` is rejected; `Speed_kmh = 121` is rejected; `Status = "DELAYED"` is rejected. The supplied ten records are accepted. |
| Student-specific observation or decision | I normalize values once during validation, so the generator, API, and analysis functions use the same clean record format. |

Accepted example:

```json
{"Timestamp":"08:10","Route":"AITU-Campus–Residence","Bus":"B01","Passengers":20,"Speed_kmh":25,"Status":"ON_ROUTE"}
```

Rejected example:

```json
{"Timestamp":"08:10","Route":"AITU-Campus–Residence","Bus":"B01","Passengers":-2,"Speed_kmh":150,"Status":"DELAYED"}
```

The rejected example returns three clear errors for passengers, speed, and status.

### 3.3 Streaming generator

| Required evidence | Student response / reference |
|---|---|
| Explanation | `event_stream()` accepts any iterable, validates one event, checks its order against only the previous timestamp, and immediately yields it. It does not call `list()` or retain the complete stream. The optional delay is only for demonstration. |
| Code / file / function reference | `shuttle.py`: `event_stream()` |
| Execution evidence / result | Iterating through the generator yields timestamps from `08:00` through `08:09`. `test_out_of_order_stream_is_rejected` confirms that `08:01` followed by `08:00` is rejected. |
| Student-specific observation or decision | I check ordering incrementally with one `previous_timestamp` variable, preserving constant memory use. |

### 3.4 Streaming simulation

| Event | Passengers | Speed | Status | Processed? | Reason |
|---:|---:|---:|---|---|---|
| 1 | 18 | 31 | ON_ROUTE | Yes | Valid event received in chronological order |
| 2 | 22 | 28 | ON_ROUTE | Yes | Valid event received in chronological order |
| 3 | 21 | 29 | ON_ROUTE | Yes | Valid event received in chronological order |
| 4 | 25 | 27 | ON_ROUTE | Yes | Valid event received in chronological order |
| 5 | 24 | 0 | STOPPED | Yes | Valid event received in chronological order; zero speed is allowed |

| Required evidence | Student response / reference |
|---|---|
| Explanation | `process_stream()` enumerates results from `event_stream()` and yields a processing record. All first five supplied events are valid, including the stopped bus with speed zero. |
| Code / file / function reference | `shuttle.py`: `process_stream()`; `main.py`: `main()` |
| Execution evidence / result | Running `python main.py` prints the five rows above before printing the analysis. |
| Student-specific observation or decision | A stopped bus is processed rather than rejected because both `STOPPED` and speed `0` satisfy the assignment rules. |

### 3.5 JSON and FastAPI endpoint

| Required evidence | Student response / reference |
|---|---|
| Explanation | `event_to_jsonable()` formats parsed time back to `HH:MM`, and `events_to_json()` produces formatted JSON. `POST /events` validates one JSON object and returns `accepted`, `errors`, and `occupancy_category`. |
| Code / file / function reference | `shuttle.py`: `event_to_jsonable()`, `events_to_json()`, `occupancy_category()`; `app.py`: `receive_event()` |
| Execution evidence / result | A request with 31 passengers returns `accepted: true`, no errors, and `OVER_CAPACITY`. A request with `Passengers: -1` returns `accepted: false`, a validation message, and a null category. |
| Student-specific observation or decision | I reused the same validation function in the API and stream to prevent two sets of rules from becoming inconsistent. |

Occupancy rules:

| Passenger count | Category |
|---:|---|
| 0–10 | LOW |
| 11–20 | MEDIUM |
| 21–30 | HIGH |
| More than 30 | OVER_CAPACITY |

### 3.6 Data analysis

| Metric | Result | Evidence |
|---|---:|---|
| Average passenger count | 24.4 | `244 total passengers / 10 events` |
| Maximum passenger count | 30 | Highest `Passengers` value |
| Number of STOPPED events | 1 | Event at `08:04` |
| Busiest minute | 08:09 | Event with 30 passengers |
| Busiest bus | B02 | Bus in the `08:09` event |

| Required evidence | Student response / reference |
|---|---|
| Explanation | `analyze_events()` calculates the total, count, stopped count, and busiest record during one pass. The average is calculated after the loop. |
| Code / file / function reference | `shuttle.py`: `analyze_events()` |
| Execution evidence / result | `python main.py` prints `24.4`, `30`, `1`, `08:09`, and `B02`. The same values are asserted in the test suite. |
| Student-specific observation or decision | I used one-pass aggregation instead of several loops so the same function can later process a large stream efficiently. |

### 3.7 Testing and code quality

| Test | Input | Expected result | Actual result | Status |
|---|---|---|---|---|
| Valid parsing | First supplied event | Parsed time `08:00`, passengers `18`, speed `31.0` | Matches expected | PASS |
| Negative passengers | `Passengers = -1` | Validation error | Correct error produced | PASS |
| Excessive speed | `Speed_kmh = 121` | Validation error | Correct error produced | PASS |
| Invalid status | `Status = DELAYED` | Validation error | Correct error produced | PASS |
| Occupancy boundaries | Counts 10, 11, 21, 31 | LOW, MEDIUM, HIGH, OVER_CAPACITY | Matches expected | PASS |
| Out-of-order stream | `08:01`, then `08:00` | Validation error | Correct error produced | PASS |
| Analysis | Ten supplied events | 24.4, 30, 1, 08:09, B02 | Matches expected | PASS |

| Required evidence | Student response / reference |
|---|---|
| Explanation | The test suite covers accepted input, rejected input, exact category boundaries, stream order, and final statistics. Functions use descriptive names and one responsibility each. |
| Code / file / function reference | `test_shuttle.py`: `ShuttleTests` (seven test methods) |
| Execution evidence / result | `python -m unittest -v` completes seven tests successfully. |
| Student-specific observation or decision | My additional test is the out-of-order stream case. It verifies a property of the stream rather than only individual field values. |

### 3.8 Technical interpretation

| Required evidence | Student response / reference |
|---|---|
| Explanation | A generator produces one event only when requested. An unlimited stream therefore does not need to fit into memory. A list would keep growing, waste memory, increase latency before processing, and eventually fail. |
| Code / file / function reference | `shuttle.py`: `event_stream()` and `analyze_events()` |
| Execution evidence / result | The generator contains `yield` and keeps only the current event, previous timestamp, and a few counters. |
| Student-specific observation or decision | The current input uses only time-of-day, so a stream crossing midnight would look out of order. A production version should use a full ISO 8601 date and time. |

## 4. Individual work and anti-plagiarism record

| Individual evidence | Student entry |
|---|---|
| My unique implementation/design decision | I perform validation, chronological checking, and statistical aggregation incrementally so the processor keeps constant memory usage. |
| My own test case | `test_out_of_order_stream_is_rejected` checks that `08:01` followed by `08:00` is rejected. |
| Bug/problem I encountered and solution | Numeric strings can appear in JSON or CSV input. I added explicit parsing while rejecting fractional passenger counts and booleans, which Python would otherwise treat like integers. |
| Exact code/repository/commit reference | `shuttle.py`, `app.py`, `test_shuttle.py`; add repository commit if required. |
| One limitation of my implementation | The timestamp contains no date, so midnight rollover is not supported. |
| One improvement I would make | Use full ISO 8601 timestamps and connect `event_stream()` to a real message broker such as Kafka if the project becomes a production system. |

## 5. Submission package checklist

- [x] Python source code
- [x] Technical report
- [x] JSON sample
- [x] FastAPI endpoint code
- [x] Completed assignment tables
- [x] At least 3 test cases
- [x] README with run instructions
- [x] Execution evidence / API responses
- [ ] Oral defense completed in person

## 6. Student declaration of originality

I confirm that this submission represents my own work. I have not copied
another student's source code, calculations, tables, screenshots, test results,
API responses, or written explanations. Any external material or reused code
has been identified. I understand that the instructor may request a live
demonstration, code modification, or explanation of any submitted component.

| Role | Name | Signature | Date |
|---|---|---|---|
| Student | Sbashev Batyrsayan | Sbashev B.M. | 14 September 2026 |
