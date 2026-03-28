"""Patient モデルのテスト."""

from datetime import date

import pytest
from pydantic import ValidationError

from dpc_simdata.models.patient import Patient, Sex


class TestPatient:
    def test_valid_patient(self, sample_patient: Patient) -> None:
        assert sample_patient.patient_id == "P0001"
        assert sample_patient.sex == Sex.MALE
        assert sample_patient.birth_date == date(1960, 5, 15)
        assert sample_patient.postal_code is None

    def test_with_postal_code(self) -> None:
        p = Patient(
            patient_id="P0002",
            birth_date=date(1980, 1, 1),
            sex=Sex.FEMALE,
            kana_name="サトウ ハナコ",
            postal_code="1000001",
        )
        assert p.postal_code == "1000001"

    def test_invalid_postal_code(self) -> None:
        with pytest.raises(ValidationError):
            Patient(
                patient_id="P0003",
                birth_date=date(1990, 6, 1),
                sex=Sex.MALE,
                kana_name="タナカ ジロウ",
                postal_code="100-0001",
            )

    def test_sex_values(self) -> None:
        assert Sex.MALE.value == "1"
        assert Sex.FEMALE.value == "2"
