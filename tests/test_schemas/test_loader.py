"""スキーマローダーのテスト."""

import pytest

from dpc_simdata.schemas.loader import load_schema


class TestLoadSchema:
    def test_load_form3(self) -> None:
        schema = load_schema("form3")
        assert schema.dataset == "form3"
        assert schema.format == "csv"
        assert schema.encoding == "shift_jis"
        assert len(schema.fields) == 10

    def test_fields_sorted_by_position(self) -> None:
        schema = load_schema("form3")
        positions = [f.position for f in schema.fields]
        assert positions == sorted(positions)

    def test_field_attributes(self) -> None:
        schema = load_schema("form3")
        facility_code_field = schema.fields[0]
        assert facility_code_field.name == "facility_code"
        assert facility_code_field.type == "string"
        assert facility_code_field.width == 10
        assert facility_code_field.required is True
        assert facility_code_field.source == "facility.facility_code"

    def test_nonexistent_schema_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_schema("nonexistent")
