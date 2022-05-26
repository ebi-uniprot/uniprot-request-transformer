import sys
from collections import defaultdict


def floor_minute(timestamp):
    return 60 * int(timestamp / 60)


def main():
    requests_per_minute = defaultdict(int)
    for timestamp in sys.stdin:
        floored = floor_minute(timestamp)
        requests_per_minute[floored] += 1
    for timestamp in sorted(requests_per_minute.keys()):
        sys.stdout.write(f"{timestamp},{requests_per_minute[timestamp]}")


if __name__ == "__main__":
    main()
