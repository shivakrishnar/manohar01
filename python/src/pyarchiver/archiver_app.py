"""CLI entrypoint for the Python port of ArchiverApp
Usage:
    python -m pyarchiver.archiver_app config.yaml
"""
import sys
import yaml
from .archiver_service import ArchiverService


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m pyarchiver.archiver_app <config.yml>")
        return 2

    config_file = argv[0]
    with open(config_file, 'r') as f:
        cfg = yaml.safe_load(f)

    svc = ArchiverService(cfg)
    svc.run_once()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
