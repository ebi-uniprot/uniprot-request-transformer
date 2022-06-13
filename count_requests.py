#!/usr/bin/env python3
import sys
import pandas as pd


def floor_minute(timestamp):
    try:
        return 60 * int(int(timestamp) / 60)
    except:
        return pd.NA


# def get_status_key(status):
#     return f"{status[0]}xx"


def main():
    header = [
        "DateTime",
        "Method",
        "Resource",
        "Namespace",
        "Status",
        "SizeBytes",
        "ResponseTime",
        "Referer",
        "UserAgentFamily",
        "IP",
    ]
    infile = sys.argv[1]
    df = pd.read_csv(
        infile,
        names=header,
        usecols=[header.index(h) for h in ["Namespace", "DateTime"]],
    ).dropna(how="all")
    namespaces = {
        "uniprot",
        "jobs",
        "proteomes",
        "uniref",
        "blast",
        "root",
        "uploadlists",
        "mapping",
        "citations",
        "taxonomy",
        "align",
        "entry",
        "basket",
        "filterhints",
        "uniparc",
        "help",
        "peptidesearch",
        "hints",
        "saas",
        "diseases",
        "keywords",
        "unirule",
        "database",
        "news",
        "arba",
        "view",
        "locations",
        "journals",
        "docs",
        "manual",
        "downloads",
    }
    df = df[df.Namespace.isin(namespaces)]
    df["DateTime"] = df["DateTime"].apply(floor_minute)
    for namespace, namespace_group in df.groupby("Namespace"):
        namespace_group.groupby("DateTime").size().to_csv(
            f"{infile}.{namespace}.rpm", header=False
        )


if __name__ == "__main__":
    main()
