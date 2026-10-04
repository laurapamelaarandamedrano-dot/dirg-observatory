"""Stage 6: display geometry for the observatory.

Analytical work uses full-resolution geometry (src/clean.py). The browser receives a simplified,
quantized TopoJSON (shared borders kept topologically consistent) plus label/node anchor points.
Anchor points are state representative points, never facility locations.
"""
from __future__ import annotations

import json

import geopandas as gpd
import topojson as tp

from .common import GEO, SITE, STATES, ISO_ALIASES, ISO_TO_CVE, get_logger, write_json

log = get_logger("geo")
TOLERANCE_DEG = 0.02   # ≈ 2 km; enough for a national-scale globe


def main() -> dict:
    g = gpd.read_file(GEO / "ne_10m_admin1_mexico.geojson")
    g["iso"] = g.iso_3166_2.replace(ISO_ALIASES)
    g["id"] = g.iso.map(ISO_TO_CVE)
    g["name"] = g.id.map(lambda c: STATES[c][1])
    g["geometry"] = g.geometry.make_valid()
    g = g[["id", "name", "iso", "geometry"]]
    topo = tp.Topology(g, prequantize=1e5, toposimplify=TOLERANCE_DEG, object_name="states")
    out = SITE / "data" / "mexico_states.topo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(topo.to_json(), encoding="utf-8")
    anchors = {}
    for r in g.itertuples():
        p = r.geometry.representative_point()
        anchors[r.id] = [round(p.x, 3), round(p.y, 3)]
    write_json(SITE / "data" / "anchors.json", anchors, compact=True)
    land_src = GEO / "world_land_110m.topo.json"
    (SITE / "data" / "land-110m.topo.json").write_text(land_src.read_text(encoding="utf-8"), encoding="utf-8")
    size = out.stat().st_size
    log.info("topojson written: %.1f KB", size / 1024)
    return {"topojson_bytes": size, "tolerance_deg": TOLERANCE_DEG}


if __name__ == "__main__":
    main()
