"""Run the whole pipeline in order. Usage: python -m src.run_pipeline [--fetch]"""
from __future__ import annotations

import sys

from . import ingest, clean, calculate_index, uncertainty, validate, build_geojson, build_docs, build_site, audit_production
from .common import get_logger

log = get_logger("pipeline")


def main(argv=None) -> int:
    """Flags:
    --fetch            download every source from its official URL, then verify against MANIFEST.csv
    --accept-updates   with --fetch: accept upstream changes and rewrite MANIFEST.csv (log it in CHANGELOG.md)
    --from-processed   skip acquisition and modelling; rebuild validation, docs and site from committed
                       data/processed outputs (used by the deploy job when official hosts are unreachable)
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--from-processed" in argv:
        return _publish()
    if "--fetch" in argv:
        ingest.fetch()
        problems = ingest.verify()
        if problems and "--accept-updates" not in argv:
            for p in problems:
                log.error(p)
            log.error("upstream sources changed; re-run with --accept-updates after review")
            return 1
        if problems:
            ingest.write_manifest("fetched by src/ingest.py --fetch (accepted update)")
    else:
        problems = ingest.verify() if ingest.MANIFEST.exists() else []
        if problems:
            for p in problems:
                log.error(p)
            return 1
        if not ingest.MANIFEST.exists():
            ingest.main(["--refresh"])
    clean.main()
    calculate_index.main()
    uncertainty.main()
    return _publish()


def _publish() -> int:
    if validate.main() != 0:
        log.error("validation failed; site not built")
        return 1
    build_geojson.main()
    build_docs.main()
    build_site.main()
    if audit_production.main() != 0:
        log.error("production audit failed; do not deploy")
        return 1
    log.info("pipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
