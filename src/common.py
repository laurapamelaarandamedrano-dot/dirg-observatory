"""Shared paths, configuration loading and the state catalogue."""
from __future__ import annotations

import hashlib
import json
import logging
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
RAW = ROOT / "data" / "raw"
DOCUMENTARY = ROOT / "data" / "documentary"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
PUBLIC = ROOT / "data" / "public"
GEO = ROOT / "geo"
REPORTS = ROOT / "reports"
SITE_SRC = ROOT / "site_src"
SITE = ROOT / "site"
DOCS = ROOT / "docs"

for _p in (INTERIM, PROCESSED, PUBLIC, REPORTS):
    _p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def load_yaml(name: str) -> dict:
    with open(CONFIG / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        if compact:
            json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        else:
            json.dump(obj, fh, ensure_ascii=False, indent=2, allow_nan=False)


def norm_text(s: str) -> str:
    """Lower-case, strip accents and extra whitespace (for joining names)."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().replace(".", " ").split())


# INEGI state code (CVE_ENT) -> (ISO 3166-2, official short name)
STATES: dict[str, tuple[str, str]] = {
    "01": ("MX-AGU", "Aguascalientes"),
    "02": ("MX-BCN", "Baja California"),
    "03": ("MX-BCS", "Baja California Sur"),
    "04": ("MX-CAM", "Campeche"),
    "05": ("MX-COA", "Coahuila"),
    "06": ("MX-COL", "Colima"),
    "07": ("MX-CHP", "Chiapas"),
    "08": ("MX-CHH", "Chihuahua"),
    "09": ("MX-CMX", "Ciudad de México"),
    "10": ("MX-DUR", "Durango"),
    "11": ("MX-GUA", "Guanajuato"),
    "12": ("MX-GRO", "Guerrero"),
    "13": ("MX-HID", "Hidalgo"),
    "14": ("MX-JAL", "Jalisco"),
    "15": ("MX-MEX", "Estado de México"),
    "16": ("MX-MIC", "Michoacán"),
    "17": ("MX-MOR", "Morelos"),
    "18": ("MX-NAY", "Nayarit"),
    "19": ("MX-NLE", "Nuevo León"),
    "20": ("MX-OAX", "Oaxaca"),
    "21": ("MX-PUE", "Puebla"),
    "22": ("MX-QUE", "Querétaro"),
    "23": ("MX-ROO", "Quintana Roo"),
    "24": ("MX-SLP", "San Luis Potosí"),
    "25": ("MX-SIN", "Sinaloa"),
    "26": ("MX-SON", "Sonora"),
    "27": ("MX-TAB", "Tabasco"),
    "28": ("MX-TAM", "Tamaulipas"),
    "29": ("MX-TLA", "Tlaxcala"),
    "30": ("MX-VER", "Veracruz"),
    "31": ("MX-YUC", "Yucatán"),
    "32": ("MX-ZAC", "Zacatecas"),
}

# Natural Earth uses MX-DIF for Mexico City.
ISO_ALIASES = {"MX-DIF": "MX-CMX"}
ISO_TO_CVE = {iso: cve for cve, (iso, _) in STATES.items()}

# Name variants found in the sources -> CVE_ENT
_NAME_VARIANTS = {
    "coahuila de zaragoza": "05",
    "michoacan de ocampo": "16",
    "veracruz de ignacio de la llave": "30",
    "mexico": "15",
    "estado de mexico": "15",
    "distrito federal": "09",
    "ciudad de mexico": "09",
    "cdmx": "09",
    "san luis potoso": "24",  # misspelling present in CNE file
    "mexicali": "02",         # municipality recorded in the state field of one CNE permit
}
NAME_TO_CVE = {norm_text(name): cve for cve, (_, name) in STATES.items()}
NAME_TO_CVE.update(_NAME_VARIANTS)


def cve_from_name(name) -> str | None:
    if name is None:
        return None
    key = norm_text(name)
    if key in NAME_TO_CVE:
        return NAME_TO_CVE[key]
    # tolerate trailing junk such as "Quintana Roo+[@[Entidad Federativa]]"
    for k, v in NAME_TO_CVE.items():
        if key.startswith(k + " ") or key.startswith(k + "+"):
            return v
    return None


def cve(x) -> str:
    return f"{int(x):02d}"
