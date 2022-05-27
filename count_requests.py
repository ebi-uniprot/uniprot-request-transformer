#!/usr/bin/env python3
import sys
from collections import defaultdict


def floor_minute(timestamp):
    return 60 * int(int(timestamp) / 60)


def get_status_key(status):
    return f"{status[0]}xx"


def main():
    requests_per_minute = defaultdict(int)
    for line in sys.stdin:
        timestamp, status, useragent = line.strip().split("|")
        floored = floor_minute(timestamp)
        requests_per_minute[(floored, get_status_key(status), useragent)] += 1
    for k in sorted(requests_per_minute.keys()):
        (timestamp, status, useragent) = k
        sys.stdout.write(f"{timestamp},{status},{requests_per_minute[k]},{useragent}\n")


if __name__ == "__main__":
    main()
