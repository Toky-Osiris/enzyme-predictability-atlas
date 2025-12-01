
import argparse
from pathlib import Path

import pandas as pd


def explode_uniprot_ids(input_tsv: str, output_tsv: str):
    """
    Take enzyme_raw.tsv and create a table with one row per EC–UniProt pair.

    Input columns (at least):
        EC_number, UniProt_IDs

    Output columns:
        EC_number, UniProt_ID
    """
    df = pd.read_csv(input_tsv, sep="\t")

    # Ensure UniProt_IDs exists
    if "UniProt_IDs" not in df.columns:
        raise ValueError("Input TSV must contain a 'UniProt_IDs' column.")

    # Split comma-separated IDs into lists
    df["UniProt_IDs"] = df["UniProt_IDs"].fillna("").astype(str)
    df["UniProt_IDs"] = df["UniProt_IDs"].apply(
        lambda s: [x for x in s.split(",") if x.strip()]
    )

    # Explode into multiple rows
    exploded = df.explode("UniProt_IDs").rename(columns={"UniProt_IDs": "UniProt_ID"})

    # Drop rows with no UniProt_ID
    exploded = exploded[exploded["UniProt_ID"].notna() & (exploded["UniProt_ID"] != "")]

    # Keep only columns you care about or leave all; here we keep EC + UniProt
    exploded = exploded[["EC_number", "UniProt_ID"]].drop_duplicates()

    out_path = Path(output_tsv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    exploded.to_csv(out_path, sep="\t", index=False)
    print(f"[explode_uniprot_ids] Saved {len(exploded)} rows to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Explode UniProt_IDs column into one row per EC–UniProt pair."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/enzyme_raw.tsv",
        help="Path to enzyme_raw.tsv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/enzyme_uniprot_pairs.tsv",
        help="Path to output TSV with EC_number, UniProt_ID",
    )

    args = parser.parse_args()
    explode_uniprot_ids(args.input, args.output)


if __name__ == "__main__":
    main()
