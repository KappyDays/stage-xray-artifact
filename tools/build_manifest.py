"""Write the deterministic release manifest after all release files are final."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage_xray_artifact.manifest import render_manifest  # noqa: E402


(ROOT / "MANIFEST.sha256").write_text(
    render_manifest(ROOT), encoding="utf-8", newline="\n"
)
print(ROOT / "MANIFEST.sha256")
