"""Facility / Ward モデルのテスト."""

import pytest
from pydantic import ValidationError

from dpc_simdata.models.facility import Facility, FacilityType, Ward, WardType


class TestFacility:
    def test_valid_facility(self, sample_facility: Facility) -> None:
        assert sample_facility.facility_code == "0112345678"
        assert sample_facility.facility_type == FacilityType.DPC_TARGET
        assert sample_facility.bed_count == 200

    def test_facility_code_must_be_10_digits(self) -> None:
        with pytest.raises(ValidationError):
            Facility(
                facility_code="012345",
                facility_name="短いコード",
                prefecture_code="01",
                facility_type=FacilityType.DPC_TARGET,
                bed_count=100,
            )

    def test_prefecture_code_must_be_2_digits(self) -> None:
        with pytest.raises(ValidationError):
            Facility(
                facility_code="0112345678",
                facility_name="テスト",
                prefecture_code="ABC",
                facility_type=FacilityType.DPC_TARGET,
                bed_count=100,
            )

    def test_bed_count_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            Facility(
                facility_code="0112345678",
                facility_name="テスト",
                prefecture_code="01",
                facility_type=FacilityType.DPC_TARGET,
                bed_count=0,
            )

    def test_frozen(self, sample_facility: Facility) -> None:
        with pytest.raises(ValidationError):
            sample_facility.bed_count = 999


class TestWard:
    def test_valid_ward(self, sample_ward: Ward) -> None:
        assert sample_ward.ward_type == WardType.GENERAL
        assert sample_ward.bed_count == 50

    def test_ward_frozen(self, sample_ward: Ward) -> None:
        with pytest.raises(ValidationError):
            sample_ward.ward_code = "99"
