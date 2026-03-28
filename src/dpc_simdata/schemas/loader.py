"""YAMLスキーマの読み込みと構造体定義."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class FieldDef:
    """1フィールドの定義."""

    name: str
    position: int
    type: str  # "string" | "integer" | "date" | "decimal"
    width: int
    required: bool
    description: str
    source: str = ""
    pattern: str = ""
    code_system: str = ""


@dataclass(frozen=True)
class DatasetSchema:
    """データセット全体のスキーマ."""

    dataset: str
    description: str
    format: str  # "csv" | "fixed_width"
    encoding: str
    record_unit: str
    fields: tuple[FieldDef, ...]
    delimiter: str = ","


_SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "schemas"


def load_schema(dataset_name: str, schemas_dir: Path | None = None) -> DatasetSchema:
    """YAMLスキーマファイルを読み込み DatasetSchema を返す."""
    base_dir = schemas_dir or _SCHEMAS_DIR
    path = base_dir / f"{dataset_name}.yaml"
    if not path.exists():
        msg = f"Schema file not found: {path}"
        raise FileNotFoundError(msg)

    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    fields = tuple(
        FieldDef(
            name=fd["name"],
            position=fd["position"],
            type=fd["type"],
            width=fd["width"],
            required=fd["required"],
            description=fd["description"],
            source=fd.get("source", ""),
            pattern=fd.get("pattern", ""),
            code_system=fd.get("code_system", ""),
        )
        for fd in raw["fields"]
    )

    return DatasetSchema(
        dataset=raw["dataset"],
        description=raw["description"],
        format=raw["format"],
        encoding=raw["encoding"],
        record_unit=raw.get("record_unit", ""),
        fields=fields,
        delimiter=raw.get("delimiter", ","),
    )
