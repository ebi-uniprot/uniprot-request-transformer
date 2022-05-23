#!/usr/bin/env python3

import sys
import os
import re
from urllib.parse import urlencode, urlparse, parse_qs, unquote


def filter_request(resource):
    re_namespace_exclude = re.compile(
        r"^/mappings?|/blast|/align|/sparql|/peptidesearch|/uploadlists", re.IGNORECASE
    )
    re_query_exclude = re.compile(
        r"yourlist:|\.rss|format=rss|job:|annotation:", re.IGNORECASE
    )
    return not (
        re_namespace_exclude.match(resource) or re_query_exclude.search(resource)
    )


def transform_request(resource):
    re_organism_taxonomy = re.compile(
        r"(?P<field>organism|taxonomy):((\".*\[(?P<id1>\d+)\]\")|(?P<id2>\d+))",
        re.IGNORECASE,
    )
    parsed_url = urlparse(resource)
    parsed_qs = parse_qs(parsed_url.query)
    if "sort" in parsed_qs and "score" in parsed_qs["sort"]:
        parsed_qs.pop("sort")
    if "query" in parsed_qs:
        query = parsed_qs["query"][0]
        if "format" not in parsed_qs:
            parsed_url = parsed_url._replace(
                path=os.path.join(parsed_url.path, "search")
            )
        m = re_organism_taxonomy.match(query)
        if m:
            field = m.group("field")
            value = m.group("id1") or m.group("id2")
            query = f"{field}_id:{value}"

        query = query.replace("ACCESSION:", "accession:")
        query = query.replace("MNEMONIC:", "mnemonic:")

        parsed_qs["query"] = query

    if "format" in parsed_qs and parsed_qs["format"][0] == "tab":
        parsed_qs["format"] = "tsv"
    if parsed_url.path.endswith(".tab"):
        parsed_url = parsed_url._replace(path=parsed_url.path.replace(".tab", ".tsv"))
    parsed_url = parsed_url._replace(query=urlencode(parsed_qs, True))
    return unquote(parsed_url.geturl())


def main():
    for request in sys.stdin:
        sys.stdout.write(transform_request(request) + "\n")


if __name__ == "__main__":
    main()
