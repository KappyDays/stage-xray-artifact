$ErrorActionPreference = 'Stop'
python -m stage_xray_artifact reproduce --data data/publication_safe --out build/reproduction --verify
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m unittest discover -s tests -v
exit $LASTEXITCODE
