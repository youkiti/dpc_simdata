"""出力ファイルのスキーマレベル検証."""

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from dpc_simdata.schemas.loader import DatasetSchema, FieldDef


@dataclass
class ValidationError:
    """検証エラー."""

    file: str
    row: int
    field: str
    message: str


def _validate_field(field_def: FieldDef, value: str, row_num: int, file_name: str) -> list[ValidationError]:
    """1フィールドの値を検証する."""
    errors: list[ValidationError] = []

    if field_def.required and not value:
        errors.append(ValidationError(file_name, row_num, field_def.name, "必須フィールドが空です"))
        return errors

    if not value:
        return errors

    if field_def.type == "integer":
        try:
            int(value)
        except ValueError:
            errors.append(ValidationError(file_name, row_num, field_def.name, f"整数でない値: {value!r}"))

    if field_def.type == "decimal":
        try:
            float(value)
        except ValueError:
            errors.append(ValidationError(file_name, row_num, field_def.name, f"数値でない値: {value!r}"))

    if len(value) > field_def.width:
        errors.append(
            ValidationError(
                file_name, row_num, field_def.name, f"桁数超過: {len(value)} > {field_def.width}"
            )
        )

    if field_def.pattern and not re.match(field_def.pattern, value):
        errors.append(
            ValidationError(
                file_name, row_num, field_def.name, f"パターン不一致: {value!r} vs {field_def.pattern}"
            )
        )

    return errors


def validate_output(output_path: Path, schema: DatasetSchema) -> list[ValidationError]:
    """出力ファイルをスキーマに従い検証する."""
    errors: list[ValidationError] = []
    file_name = output_path.name

    if not output_path.exists():
        errors.append(ValidationError(file_name, 0, "", "ファイルが存在しません"))
        return errors

    sorted_fields = sorted(schema.fields, key=lambda f: f.position)
    expected_cols = len(sorted_fields)

    with output_path.open(encoding=schema.encoding) as f:
        reader = csv.reader(f, delimiter=schema.delimiter)
        for row_num, row in enumerate(reader, start=1):
            if len(row) != expected_cols:
                errors.append(
                    ValidationError(file_name, row_num, "", f"列数不一致: {len(row)} != {expected_cols}")
                )
                continue

            for field_def, value in zip(sorted_fields, row, strict=True):
                errors.extend(_validate_field(field_def, value, row_num, file_name))

    return errors
