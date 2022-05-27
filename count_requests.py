#!/usr/bin/env python3
import sys
from collections import defaultdict
from user_agents import parse


def floor_minute(timestamp):
    return 60 * int(int(timestamp) / 60)


def get_status_key(status):
    return f"{status[0]}xx"


def main():
    requests_per_minute = defaultdict(int)
    for line in sys.stdin:
        timestamp, status, useragent = line.strip().split("|")
        parsed = parse(useragent)
        useragent_family = parsed.browser.family
        floored = floor_minute(timestamp)
        requests_per_minute[(floored, get_status_key(status), useragent_family)] += 1
    for k in sorted(requests_per_minute.keys()):
        (timestamp, status, useragent_family) = k
        sys.stdout.write(
            f"{timestamp},{status},{requests_per_minute[k]},{useragent_family}\n"
        )


if __name__ == "__main__":
    main()
