import argparse
from pathlib import Path

from .parse_enzyme_core import parse_enzyme_dat


def main():
    parser = argparse.ArgumentParser(
        description="Parse ENZYME flatfile (enzyme.dat) into a tidy TSV."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/enzyme.dat",
        help="Path to enzyme.dat (default: data/raw/enzyme.dat)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/enzyme_raw.tsv",
        help="Path to output TSV (default: data/processed/enzyme_raw.tsv)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[parse_enzyme] Reading: {input_path}")
    df = parse_enzyme_dat(input_path)
    print(f"[parse_enzyme] Parsed {len(df)} EC entries.")

    df.to_csv(output_path, sep="\t", index=False)
    print(f"[parse_enzyme] Saved: {output_path}")


if __name__ == "__main__":
    main()
