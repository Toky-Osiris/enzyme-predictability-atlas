import argparse
import pandas as pd
from pathlib import Path


def find_missing_ids(pairs_tsv: str, uniprot_tsv: str, output_tsv: str):
    pairs = pd.read_csv(pairs_tsv, sep="\t")
    uni = pd.read_csv(uniprot_tsv, sep="\t")

    all_ids = set(pairs["UniProt_ID"].dropna().astype(str).unique())
    got_ids = set(uni["UniProt_ID"].dropna().astype(str).unique())

    missing = sorted(all_ids - got_ids)
    print(f"Total unique IDs in pairs:  {len(all_ids)}")
    print(f"Total unique IDs downloaded: {len(got_ids)}")
    print(f"Missing IDs: {len(missing)}")

    out_df = pd.DataFrame({"UniProt_ID": missing})
    out_path = Path(output_tsv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, sep="\t", index=False)
    print(f"Saved missing IDs to: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Find UniProt IDs present in enzyme_uniprot_pairs.tsv but missing in uniprot_sequences.tsv"
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
        default="data/processed/uniprot_sequences.tsv",
        help="Path to uniprot_sequences.tsv (downloaded so far)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/uniprot_missing_ids.tsv",
        help="Path to output TSV containing missing UniProt_ID column",
    )
    args = parser.parse_args()

    find_missing_ids(args.pairs, args.uniprot, args.output)


if __name__ == "__main__":
    main()
