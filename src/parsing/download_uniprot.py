import argparse
from pathlib import Path
from time import sleep
from typing import List

import pandas as pd
import requests


UNIPROT_SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"


def chunk_list(items: List[str], chunk_size: int) -> List[List[str]]:
    """Split a list into chunks of size chunk_size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def build_accession_query(accessions: List[str]) -> str:
    """
    Build a UniProt query string like:
    accession:C0IPP2 OR accession:C0IW58 OR ...
    """
    parts = [f"accession:{acc}" for acc in accessions]
    return " OR ".join(parts)


def fetch_uniprot_batch(accessions: List[str]) -> pd.DataFrame:
    """
    Fetch a batch of UniProt entries as TSV for a list of accessions.

    Returns a DataFrame with at least:
        UniProt_ID, Sequence, Length, Organism, Protein_name, Gene_name
    or an empty DataFrame on failure / no matches.
    """
    if not accessions:
        return pd.DataFrame()

    query = build_accession_query(accessions)

    params = {
    "query": query,
    "format": "tsv",
    "fields": ",".join(
        [
            "accession",
            "organism_name",
            "protein_name",
            "gene_primary",
            "sequence",
            "length",
        ]
    ),
    "size": 499,  # allow up to 500 results per query (max per request)
}

    try:
        resp = requests.get(UNIPROT_SEARCH_URL, params=params, timeout=30)
    except Exception as e:
        print(f"[fetch_uniprot_batch] Request error for batch of {len(accessions)} IDs: {e}")
        print(f"  Query (truncated): {query[:200]}...")
        return pd.DataFrame()

    if resp.status_code != 200:
        print(f"[fetch_uniprot_batch] HTTP {resp.status_code} for batch of {len(accessions)} IDs")
        print(f"  Query (truncated): {query[:200]}...")
        print(f"  Response (first 300 chars): {resp.text[:300]!r}")
        return pd.DataFrame()

    text = resp.text.strip()
    if not text:
        # This means UniProt returned a valid response but no hits
        print(f"[fetch_uniprot_batch] No matches for batch of {len(accessions)} IDs.")
        return pd.DataFrame()

    from io import StringIO
    df = pd.read_csv(StringIO(text), sep="\t")

    # Align UniProt column names to our internal names
    rename_map = {
        "Entry": "UniProt_ID",
        "Accession": "UniProt_ID",
        "Organism": "Organism",
        "Organism (scientific name)": "Organism",
        "Organism [Organism]": "Organism",
        "Protein names": "Protein_name",
        "Protein name": "Protein_name",
        "Gene Names": "Gene_name",
        "Gene Names (primary)": "Gene_name",
        "Gene Names (primary name)": "Gene_name",
        "Sequence": "Sequence",
        "Length": "Length",
    }

    for old, new in rename_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)

    expected = ["UniProt_ID", "Sequence", "Length", "Organism", "Protein_name", "Gene_name"]
    for col in expected:
        if col not in df.columns:
            df[col] = pd.NA

    return df[expected]


def download_uniprot_batch(
    pairs_tsv: str,
    output_tsv: str,
    chunk_size: int = 50,
    sleep_sec: float = 0.5,
):
    """
    Read enzyme_uniprot_pairs.tsv, fetch UniProt TSV data in batches,
    and write a table of sequences and metadata.
    """
    df_pairs = pd.read_csv(pairs_tsv, sep="\t")

    if "UniProt_ID" not in df_pairs.columns:
        raise ValueError("Input TSV must contain a 'UniProt_ID' column.")

    unique_ids = sorted(df_pairs["UniProt_ID"].dropna().unique())
    print(f"[download_uniprot] Found {len(unique_ids)} unique UniProt IDs.")

    chunks = chunk_list(unique_ids, chunk_size)
    print(f"[download_uniprot] Split into {len(chunks)} chunks of up to {chunk_size} IDs.")

    all_dfs = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"[download_uniprot] Chunk {i}/{len(chunks)} (n={len(chunk)})")
        df_chunk = fetch_uniprot_batch(chunk)
        if not df_chunk.empty:
            all_dfs.append(df_chunk)
            print(f"[download_uniprot]   Retrieved {len(df_chunk)} rows.")
        else:
            print(f"[download_uniprot]   Warning: empty result for chunk {i}")
        sleep(sleep_sec)

    if not all_dfs:
        print("[download_uniprot] No data fetched at all; not writing output file.")
        return

    df_all = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=["UniProt_ID"])
    out_path = Path(output_tsv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df_all.to_csv(out_path, sep="\t", index=False)
    print(f"[download_uniprot] Saved {len(df_all)} entries to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Download UniProt sequences and metadata for EC–UniProt pairs using batched queries."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/enzyme_uniprot_pairs.tsv",
        help="Path to enzyme_uniprot_pairs.tsv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/uniprot_sequences.tsv",
        help="Path to output TSV with UniProt metadata and sequences",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50,
        help="Number of IDs per UniProt request (default: 50)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Sleep time between requests in seconds (default: 0.5)",
    )

    args = parser.parse_args()
    download_uniprot_batch(
        args.input,
        args.output,
        chunk_size=args.chunk_size,
        sleep_sec=args.sleep,
    )


if __name__ == "__main__":
    main()
