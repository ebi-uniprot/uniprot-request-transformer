#!/usr/bin/env python3
from transformer import include_request, transform_request


def main():
    with open("tests/input.txt") as f:
        input_requests = f.readlines()
    included = [r for r in input_requests if include_request(r)]
    transformed = [transform_request(r) for r in included]
    with open("tests/expected.txt") as f:
        expected_requests = [l.strip() for l in f.readlines()]
    assert len(transformed) == len(expected_requests)
    for n, [e, t] in enumerate(zip(expected_requests, transformed)):
        assert e == t, f"FAIL line {n + 1}\n{e}\n!=\n{t}"
    print("PASS")


if __name__ == "__main__":
    main()
