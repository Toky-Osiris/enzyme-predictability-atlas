import argparse
from pathlib import Path

import pandas as pd


def merge_enzyme_uniprot(
    enzyme_raw_tsv: str,
    pairs_tsv: str,
    uniprot_tsv: str,
    output_tsv: str,
):
    """
    Build a master table linking EC numbers, UniProt IDs, sequences, and ENZYME metadata.

    Inputs:
        enzyme_raw_tsv: data/processed/enzyme_raw.tsv
        pairs_tsv:      data/processed/enzyme_uniprot_pairs.tsv
        uniprot_tsv:    data/processed/uniprot_sequences_merged.tsv (or uniprot_sequences.tsv)
    Output:
        output_tsv:     data/processed/enzyme_master.tsv
    """
    enzyme_raw = pd.read_csv(enzyme_raw_tsv, sep="\t")
    pairs = pd.read_csv(pairs_tsv, sep="\t")
    uniprot = pd.read_csv(uniprot_tsv, sep="\t")

    # Merge EC metadata onto EC–UniProt pairs
    # enzyme_raw has one row per EC_number; pairs has EC_number, UniProt_ID
    ec_meta = enzyme_raw[
        ["EC_number", "Enzyme_name", "Alt_names", "Reaction", "Prosite_refs"]
    ].drop_duplicates()

    df = pairs.merge(ec_meta, on="EC_number", how="left")

    # Merge UniProt sequences and metadata
    df = df.merge(uniprot, on="UniProt_ID", how="left")

    # Basic cleaning: drop rows with missing sequence
    n_before = len(df)
    df = df[df["Sequence"].notna() & (df["Sequence"].astype(str) != "")]
    n_after = len(df)
    print(f"[merge_enzyme_uniprot] Dropped {n_before - n_after} rows with missing sequences.")

    out_path = Path(output_tsv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_path, sep="\t", index=False)
    print(f"[merge_enzyme_uniprot] Saved {len(df)} rows to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge ENZYME and UniProt tables into a master enzyme dataset."
    )
    parser.add_argument(
        "--enzyme-raw",
        type=str,
        default="data/processed/enzyme_raw.tsv",
        help="Path to enzyme_raw.tsv",
    )
    parser.add_argument(
        "--pairs",
        type=str,
        default="data/processed/enzyme_uniprot_pairs.tsv",
        help="Path to enzyme_uniprot_pairs.tsv",
    )
    parser.add_argument(
        "--uniprot",
        type=str,
        default="data/processed/uniprot_sequences_merged.tsv",
        help="Path to uniprot_sequences.tsv or uniprot_sequences_merged.tsv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/enzyme_master.tsv",
        help="Path to output master TSV",
    )

    args = parser.parse_args()
    merge_enzyme_uniprot(
        args.enzyme_raw,
        args.pairs,
        args.uniprot,
        args.output,
    )


if __name__ == "__main__":
    main()
