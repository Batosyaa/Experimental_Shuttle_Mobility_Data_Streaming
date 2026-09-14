"""Short command-line demonstration for the oral defense."""

from shuttle import SHUTTLE_EVENTS, analyze_events, process_stream


def main() -> None:
    print("FIRST FIVE STREAM RESULTS")
    for result in process_stream(SHUTTLE_EVENTS[:5]):
        print(result)

    print("\nANALYSIS")
    for name, value in analyze_events(SHUTTLE_EVENTS).items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
