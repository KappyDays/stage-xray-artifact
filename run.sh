#!/usr/bin/env sh
set -eu
python -m stage_xray_artifact reproduce --data data/publication_safe --out build/reproduction --verify
python -m unittest discover -s tests -v
