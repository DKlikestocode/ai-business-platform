import json
from pathlib import Path

FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1] / "fixtures" / "shk-anfragen-testpaket-v1"
)
CASE_DIRECTORIES = tuple(sorted((FIXTURE_ROOT / "cases").glob("case_*")))
def load_expected(case_directory: Path) -> dict:
    return json.loads((case_directory / "expected.json").read_text(encoding="utf-8"))
