#!/usr/bin/env python3

import sys
import os
import re
from urllib.parse import urlencode, urlparse, parse_qs, unquote


def include_request(resource):
    re_namespace_exclude = re.compile(
        r"^/mappings?|/blast|/align|/sparql|/peptidesearch|/uploadlists", re.IGNORECASE
    )
    re_query_exclude = re.compile(
        r"yourlist:|\.rss|format=rss|job:|annotation:", re.IGNORECASE
    )
    return not (
        re_namespace_exclude.match(resource) or re_query_exclude.search(resource)
    )


def transorm_date(date):
    if date == "*" or len(date) != 8:
        return "*"
    return f"{date[:4]}-{date[4:6]}-{date[6:8]}"


def transform_query(query):
    re_organism_taxonomy = re.compile(
        r"(?P<field>organism|taxonomy):((\".*\[(?P<id1>\d+)\]\")|(?P<id2>\d+))",
        re.IGNORECASE,
    )
    re_created = re.compile(r"created:\[(?P<start>.*) TO (?P<end>.*)]")

    m = re_organism_taxonomy.match(query)
    if m:
        field = m.group("field")
        value = m.group("id1") or m.group("id2")
        return f"{field}_id:{value}"

    m = re_created.match(query)
    if m:
        start = transorm_date(m.group("start"))
        end = transorm_date(m.group("end"))
        return f"date_created:{start} TO {end}"

    query = query.replace("ACCESSION:", "accession:")
    query = query.replace("MNEMONIC:", "mnemonic:")

    return query


def transform_request(resource):
    parsed_url = urlparse(resource)
    parsed_qs = parse_qs(parsed_url.query)
    if "sort" in parsed_qs and "score" in parsed_qs["sort"]:
        parsed_qs.pop("sort")
    if "query" in parsed_qs:
        if "format" not in parsed_qs:
            parsed_url = parsed_url._replace(
                path=os.path.join(parsed_url.path, "search")
            )
        parsed_qs["query"] = transform_query(parsed_qs["query"][0])
    if "format" in parsed_qs and parsed_qs["format"][0] == "tab":
        parsed_qs["format"] = "tsv"
    if parsed_url.path.endswith(".tab"):
        parsed_url = parsed_url._replace(path=parsed_url.path.replace(".tab", ".tsv"))
    if parsed_url.path.startswith("/uniprot/"):
        parsed_url = parsed_url._replace(
            path=parsed_url.path.replace("/uniprot/", "/uniprotkb/", 1)
        )
    parsed_url = parsed_url._replace(query=urlencode(parsed_qs, True))
    return unquote(parsed_url.geturl()) + "\n"


def main():
    for request in sys.stdin:
        if include_request(request):
            sys.stdout.write(transform_request(request))


if __name__ == "__main__":
    main()
