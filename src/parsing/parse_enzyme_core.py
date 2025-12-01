from pathlib import Path
from typing import Union
import re

import pandas as pd


def parse_enzyme_dat(path: Union[str, Path]) -> pd.DataFrame:
    """
    Parse the ENZYME flatfile (enzyme.dat) into a tidy DataFrame.

    Extracts:
        - EC_number      (ID)
        - Enzyme_name    (DE)
        - Alt_names      (AN)
        - Reaction       (CA)
        - Prosite_refs   (PR)
        - UniProt_IDs    (DR, UniProt accessions only, comma-separated)

    Args:
        path: Path to enzyme.dat.

    Returns:
        pandas.DataFrame with one row per EC entry.
    """
    path = Path(path)
    rows = []

    # Current entry accumulator
    current = {
        "EC_number": None,
        "Enzyme_name": [],
        "Alt_names": [],
        "Reaction": [],
        "Prosite_refs": [],
        "UniProt_IDs": [],
    }

    def flush_entry():
        """Helper to convert current entry into a row."""
        if current["EC_number"] is None:
            return

        rows.append(
            {
                "EC_number": current["EC_number"],
                "Enzyme_name": " ".join(current["Enzyme_name"]) or None,
                "Alt_names": " ".join(current["Alt_names"]) or None,
                "Reaction": " ".join(current["Reaction"]) or None,
                "Prosite_refs": "; ".join(current["Prosite_refs"]) or None,
                "UniProt_IDs": ",".join(current["UniProt_IDs"]) or None,
            }
        )

        # reset
        current["EC_number"] = None
        current["Enzyme_name"] = []
        current["Alt_names"] = []
        current["Reaction"] = []
        current["Prosite_refs"] = []
        current["UniProt_IDs"] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            # Strip newline only
            line = line.rstrip("\n")
            if not line:
                continue

            code = line[:2]  # 'ID', 'DE', 'AN', 'CA', 'PR', 'DR', etc.
            content = line[5:].strip()  # after 'XX   '

            if code == "ID":
                # New entry; if we already had one, flush it
                if current["EC_number"] is not None:
                    flush_entry()
                # Example: "1.1.1.1"
                parts = content.split()
                current["EC_number"] = parts[0] if parts else None

            elif code == "DE":
                current["Enzyme_name"].append(content)

            elif code == "AN":
                current["Alt_names"].append(content)

            elif code == "CA":
                current["Reaction"].append(content)

            elif code == "PR":
                # PROSITE or related cross-references (e.g. PDOCxxxx)
                current["Prosite_refs"].append(content)

            elif code == "DR":
                # Database references – here we care about UniProt accessions
                # Example line:
                # DR   P00561, AK1H_ECOLI ;  P27725, AK1H_SERMA ;  P00562, AK2H_ECOLI ;
                # We want P00561, P27725, P00562, but NOT things like PS00001 (PROSITE)
                # Use a regex that excludes tokens starting with PS.
                candidates = re.findall(r"\b([A-Z0-9]{6})\b", content)
                for acc in candidates:
                    if not acc.startswith("PS"):  # avoid PROSITE pattern IDs
                        current["UniProt_IDs"].append(acc)

            elif code == "//":
                # End of entry
                flush_entry()

        # In case the file does not end with '//'
        flush_entry()

    df = pd.DataFrame(rows)
    return df
