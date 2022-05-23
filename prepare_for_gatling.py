#!/usr/bin/env python3

import sys
import re
from urllib.parse import urlparse, parse_qs


def prepare_for_gatling(resource):
    ext_to_media_type = {
        "fasta": "text/plain; format=fasta",
        "tsv": "text/plain; format=tsv",
        "xlsx": "application/vnd.ms-excel",
        "xml": "application/xml",
        "rdf": "application/rdf+xml",
        "txt": "text/plain; format=flatfile",
        "gff": "text/plain; format=gff",
        "list": "text/plain; format=list",
        "json": "application/json",
        "obo": "text/plain; format=obo",
    }

    re_ext = re.compile(
        r"\.(?P<ext>fasta|tsv|xlsx|xml|rdf|txt|gff|list|json|obo)", re.IGNORECASE
    )
    parsed_url = urlparse(resource)
    parsed_qs = parse_qs(parsed_url.query)
    m = re_ext.search(resource)
    if (
        "query" in parsed_qs
        and "format" in parsed_qs
        and parsed_qs["format"][0] in ext_to_media_type
    ):
        media_type = ext_to_media_type[parsed_qs["format"][0]]
        resource = f"{resource}#{media_type}"
    elif m and m.group("ext") in ext_to_media_type:
        media_type = ext_to_media_type[m.group("ext")]
        resource = f"{resource}#{media_type}"
    else:
        media_type = ext_to_media_type["json"]
        resource = f"{resource}#{media_type}"
    return resource


def main():
    sys.stdout.write("url#format\n")
    for request in sys.stdin:
        sys.stdout.write(prepare_for_gatling(request.strip()) + "\n")


if __name__ == "__main__":
    main()
