"""スキーマバリデーターのテスト."""

import csv
from pathlib import Path

from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.validators.schema_validator import validate_output


class TestSchemaValidator:
    def test_valid_file_no_errors(self, tmp_path: Path) -> None:
        schema = load_schema("form3")
        path = tmp_path / "form3.csv"
        with path.open("w", encoding="shift_jis", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "0112345678", "202504", "01", "一般病棟",
                "50", "01", "急性期一般入院料1", "01", "200", "01",
            ])
        errors = validate_output(path, schema)
        assert errors == []

    def test_missing_required_field(self, tmp_path: Path) -> None:
        schema = load_schema("form3")
        path = tmp_path / "form3.csv"
        with path.open("w", encoding="shift_jis", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "", "202504", "01", "一般病棟",
                "50", "01", "急性期一般入院料1", "01", "200", "01",
            ])
        errors = validate_output(path, schema)
        assert len(errors) == 1
        assert "必須" in errors[0].message

    def test_wrong_column_count(self, tmp_path: Path) -> None:
        schema = load_schema("form3")
        path = tmp_path / "form3.csv"
        with path.open("w", encoding="shift_jis", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["0112345678", "202504"])
        errors = validate_output(path, schema)
        assert any("列数" in e.message for e in errors)

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        schema = load_schema("form3")
        errors = validate_output(tmp_path / "missing.csv", schema)
        assert len(errors) == 1
        assert "存在しません" in errors[0].message
