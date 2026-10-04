"""Assemble the Dataverse deposit zip from the public layer and documentation (no raw files)."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.build_site import VERSION  # noqa: E402

FILES = sorted((ROOT / "data" / "public").glob("*.csv")) + [
    ROOT / "reports" / "QUALITY_REPORT.md", ROOT / "reports" / "production_audit.json", ROOT / "reports" / "quality_report.json",
    ROOT / "data" / "raw" / "MANIFEST.csv", ROOT / "CITATION.cff", ROOT / "CHANGELOG.md", ROOT / "LICENSE-DATA", ROOT / "README.md",
] + [ROOT / "dist" / f"DIRG_Observatory_v{VERSION}.xlsx"] + [ROOT / "docs" / f for f in ("METHODOLOGY.md", "DATA_DICTIONARY.md", "SOURCES.md", "DATA_GOVERNANCE_AUDIT.md", "LEGAL_LAYER.md", "RESEARCH_DESIGN.md", "ROADMAP.md")]


def main() -> Path:
    out = ROOT / "dist" / f"dirg-observatory-v{VERSION}-dataverse.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            if not f.exists():
                raise FileNotFoundError(f)
            z.write(f, f"dirg-observatory-v{VERSION}/{f.name}")
    print(out, out.stat().st_size)
    return out


if __name__ == "__main__":
    main()
