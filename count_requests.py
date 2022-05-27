#!/usr/bin/env python3
import sys
from collections import defaultdict


def floor_minute(timestamp):
    return 60 * int(int(timestamp) / 60)


def get_status_key(status):
    return f"{status}xx"


def main():
    requests_per_minute = defaultdict(int)
    for line in sys.stdin:
        timestamp, status = line.split("|")
        floored = floor_minute(timestamp)
        requests_per_minute[(floored, get_status_key(status))] += 1
    for k in sorted(requests_per_minute.keys()):
        (timestamp, status) = k
        sys.stdout.write(",".join([timestamp, status, requests_per_minute[k]]))


if __name__ == "__main__":
    main()
