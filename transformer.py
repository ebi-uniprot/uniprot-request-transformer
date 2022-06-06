#!/usr/bin/env python3
import sys
import os
import re
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import pandas as pd
import numpy as np

prev_to_new_return_field = {
    "id": "accession",
    "entry name": "id",
    "genes": "gene_names",
    "genes(PREFERRED)": "gene_primary",
    "genes(ALTERNATIVE)": "gene_synonym",
    "genes(OLN)": "gene_oln",
    "genes(ORF)": "gene_orf",
    "organism": "organism_name",
    "organism-id": "organism_id",
    "protein names": "protein_name",
    "proteome": "xref_proteomes",
    "lineage(ALL)": "lineage",
    "virus hosts": "virus_hosts",
    "comment(ALTERNATIVE PRODUCTS)": "cc_alternative_products",
    "feature(ALTERNATIVE SEQUENCE)": "ft_var_seq",
    "comment(ERRONEOUS GENE MODEL PREDICTION)": "error_gmodel_pred",
    "fragment": "fragment",
    "encodedon": "organelle",
    "length": "length",
    "mass": "mass",
    "comment(MASS SPECTROMETRY)": "cc_mass_spectrometry",
    "feature(NATURAL VARIANT)": "ft_variant",
    "feature(NON ADJACENT RESIDUES)": "ft_non_cons",
    "feature(NON STANDARD RESIDUE)": "ft_non_std",
    "feature(NON TERMINAL RESIDUE)": "ft_non_ter",
    "comment(POLYMORPHISM)": "cc_polymorphism",
    "comment(RNA EDITING)": "cc_rna_editing",
    "sequence": "sequence",
    "comment(SEQUENCE CAUTION)": "cc_sequence_caution",
    "feature(SEQUENCE CONFLICT)": "ft_conflict",
    "feature(SEQUENCE UNCERTAINTY)": "ft_unsure",
    "version(sequence)": "sequence_version",
    "comment(ABSORPTION)": "absorption",
    "feature(ACTIVE SITE)": "ft_act_site",
    "comment(ACTIVITY REGULATION)": "cc_activity_regulation",
    "feature(BINDING SITE)": "ft_binding",
    "chebi": "ft_ca_bind",
    "chebi(Catalytic activity)": "cc_catalytic_activity",
    "chebi(Cofactor)": "cc_cofactor",
    "feature(DNA BINDING)": "ft_dna_bind",
    "ec": "ec",
    "comment(FUNCTION)": "cc_function",
    "comment(KINETICS)": "kinetics",
    "feature(METAL BINDING)": "ft_metal",
    "feature(NP BIND)": "ft_np_bind",
    "comment(PATHWAY)": "cc_pathway",
    "comment(PH DEPENDENCE)": "ph_dependence",
    "comment(REDOX POTENTIAL)": "redox_potential",
    "rhea-id": "rhea_id",
    "feature(SITE)": "ft_site",
    "comment(TEMPERATURE DEPENDENCE)": "temp_dependence",
    "annotation score": "annotation_score",
    "comment(CAUTION)": "cc_caution",
    "features": "feature",
    "keyword-id": "keywordid",
    "keywords": "keyword",
    "comment(MISCELLANEOUS)": "cc_miscellaneous",
    "existence": "protein_existence",
    "reviewed": "reviewed",
    "tools": "tools",
    "uniparcid": "uniparc_id",
    "interactor": "cc_interaction",
    "comment(SUBUNIT)": "cc_subunit",
    "comment(DEVELOPMENTAL STAGE)": "cc_developmental_stage",
    "comment(INDUCTION)": "cc_induction",
    "comment(TISSUE SPECIFICITY)": "cc_tissue_specificity",
    "go(biological process)": "go_p",
    "go(cellular component)": "go_c",
    "go": "go",
    "go(molecular function)": "go_f",
    "go-id": "go_id",
    "comment(ALLERGEN)": "cc_allergen",
    "comment(BIOTECHNOLOGY)": "cc_biotechnology",
    "comment(DISRUPTION PHENOTYPE)": "cc_disruption_phenotype",
    "comment(DISEASE)": "cc_disease",
    "feature(MUTAGENESIS)": "ft_mutagen",
    "comment(PHARMACEUTICAL)": "cc_pharmaceutical",
    "comment(TOXIC DOSE)": "cc_toxic_dose",
    "feature(INTRAMEMBRANE)": "ft_intramem",
    "comment(SUBCELLULAR LOCATION)": "cc_subcellular_location",
    "feature(TOPOLOGICAL DOMAIN)": "ft_topo_dom",
    "feature(TRANSMEMBRANE)": "ft_transmem",
    "feature(CHAIN)": "ft_chain",
    "feature(CROSS LINK)": "ft_crosslnk",
    "feature(DISULFIDE BOND)": "ft_disulfid",
    "feature(GLYCOSYLATION)": "ft_carbohyd",
    "feature(INITIATOR METHIONINE)": "ft_init_met",
    "feature(LIPIDATION)": "ft_lipid",
    "feature(MODIFIED RESIDUE)": "ft_mod_res",
    "feature(PEPTIDE)": "ft_peptide",
    "comment(PTM)": "cc_ptm",
    "feature(PROPEPTIDE)": "ft_propep",
    "feature(SIGNAL)": "ft_signal",
    "feature(TRANSIT)": "ft_transit",
    "3d": "structure_3d",
    "feature(BETA STRAND)": "ft_strand",
    "feature(HELIX)": "ft_helix",
    "feature(TURN)": "ft_turn",
    "citation": "lit_pubmed_id",
    "created": "date_created",
    "last-modified": "date_modified",
    "sequence-modified": "date_sequence_modified",
    "version(entry)": "version",
    "feature(COILED COIL)": "ft_coiled",
    "feature(COMPOSITIONAL BIAS)": "ft_compbias",
    "comment(DOMAIN)": "cc_domain",
    "feature(DOMAIN EXTENT)": "ft_domain",
    "feature(MOTIF)": "ft_motif",
    "families": "protein_families",
    "feature(REGION)": "ft_region",
    "feature(REPEAT)": "ft_repeat",
    "feature(ZINC FINGER)": "ft_zn_fing",
}


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
    m = re_organism_taxonomy.search(query)
    if m:
        field = m.group("field")
        value = m.group("id1") or m.group("id2")
        return f"{field}_id:{value}"

    re_created = re.compile(r"created:\[(?P<start>.*) TO (?P<end>.*)]", re.IGNORECASE)
    m = re_created.search(query)
    if m:
        start = transorm_date(m.group("start"))
        end = transorm_date(m.group("end"))
        return f"date_created:{start} TO {end}"

    re_database = re.compile(
        r"database:\(type:(?P<db>\S*)(( count:\[(?P<start>.*) TO (?P<end>.*)\])| (?P<qid>.*))?\)",
        re.IGNORECASE,
    )
    m = re_database.search(query)
    if m:
        db = m.group("db")
        start = m.group("start")
        end = m.group("end")
        qid = m.group("qid")
        if start and end:
            return f"xref_count_{db}:[{start} TO {end}]"
        if qid:
            return f"xref:{db}-{qid}"
        return f"database:{db}"

    prev_to_new_query_field = {
        "author": "lit_author",
        "cdantigen": "protein_name",
        "entry_name": "protein_name",
        "goa": "go",
        "host": "virus_host",
        "id": "accession_id",
        "inn": "protein_name",
        "method": "cc_mass_spectrometry",
        "modified": "date_modified",
        "name": "protein_name",
        "replaces": "sec_acc",
        "sequence_modified": "date_sequence_modified",
        "web": "cc_webresource",
    }
    for prev_field, new_field in prev_to_new_query_field.items():
        query = query.replace(f"{prev_field}:", f"{new_field}:")

    query = query.replace("ACCESSION:", "accession:")
    query = query.replace("MNEMONIC:", "id:")
    query = query.replace("mnemonic:", "id:")

    return query


def transform_columns(columns):
    return ",".join(
        [
            prev_to_new_return_field[c]
            for c in columns.split(",")
            if c in prev_to_new_return_field
        ]
    )


def transform_request(resource):
    parsed_url = urlparse(resource)
    parsed_qs = parse_qs(parsed_url.query)
    if "sort" in parsed_qs:
        if "score" in parsed_qs["sort"]:
            parsed_qs.pop("sort")
        else:
            sort_field = parsed_qs["sort"][0]
            if sort_field in prev_to_new_return_field:
                sort_field = prev_to_new_return_field[sort_field]
                sort_dir = (
                    "asc"
                    if "desc" in parsed_qs and parsed_qs["desc"][0] == "no"
                    else "desc"
                )
                parsed_qs["sort"] = f"{sort_field} {sort_dir}"
    if "query" in parsed_qs:
        endpoint = (
            "stream" if "format" in parsed_qs and "limit" not in parsed_qs else "search"
        )
        parsed_url = parsed_url._replace(path=os.path.join(parsed_url.path, endpoint))
        parsed_qs["query"] = transform_query(parsed_qs["query"][0])
    if "format" in parsed_qs and parsed_qs["format"][0] == "tab":
        parsed_qs["format"] = "tsv"
    if parsed_url.path.endswith(".tab"):
        parsed_url = parsed_url._replace(path=parsed_url.path.replace(".tab", ".tsv"))
    if "compress" in parsed_qs:
        parsed_qs["compressed"] = (
            "true" if parsed_qs["compress"][0] == "yes" else "false"
        )
        del parsed_qs["compress"]
    if "limit" in parsed_qs:
        parsed_qs["size"] = parsed_qs["limit"]
        del parsed_qs["limit"]
    if "columns" in parsed_qs:
        transformed_columns = transform_columns(parsed_qs["columns"][0])
        if len(transformed_columns):
            parsed_qs["fields"] = transformed_columns
        del parsed_qs["columns"]
    if parsed_url.path.startswith("/uniprot/"):
        parsed_url = parsed_url._replace(
            path=parsed_url.path.replace("/uniprot/", "/uniprotkb/", 1)
        )
    if parsed_url.path.endswith("/protvista"):
        parsed_url = parsed_url._replace(path=parsed_url.path.replace("/protvista", ""))
    p = re.compile(r"&format=(?P<format>.+)")
    m = p.search(parsed_url.path)
    if m:
        parsed_url = parsed_url._replace(path=re.sub(p, "", parsed_url.path))
        parsed_qs["format"] = m.group("format")
    parsed_url = parsed_url._replace(query=urlencode(parsed_qs, True))
    return unquote(parsed_url.geturl())


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
    assert len(sys.argv) == 3
    infile = sys.argv[1]
    outfile = sys.argv[2]
    header = [
        "DateTime",
        "Method",
        "Resource",
        "Status",
        "SizeBytes",
        "ResponseTime",
        "Referer",
        "UserAgentFamily",
    ]
    df = pd.read_csv(
        infile,
        names=header,
        usecols=[header.index(h) for h in ["Resource", "Method", "Status"]],
    )
    df = df[
        (df["Method"] == "GET")
        & (df["Status"] == 200)
        & df["Resource"].apply(include_request)
    ]
    df["Transformed"] = df["Resource"].apply(
        lambda r: prepare_for_gatling(transform_request(r))
    )
    np.savetxt(outfile, df["Transformed"], fmt='%s')


if __name__ == "__main__":
    main()
