"""共通テストフィクスチャ."""

from datetime import date

import pytest

from dpc_simdata.generators.seed import SeedManager
from dpc_simdata.models.admission import AdmissionEpisode, AdmissionRoute, PayerType
from dpc_simdata.models.facility import Facility, FacilityType, Ward, WardType
from dpc_simdata.models.patient import Patient, Sex


@pytest.fixture
def seed_manager() -> SeedManager:
    return SeedManager(root_seed=42)


@pytest.fixture
def sample_facility() -> Facility:
    return Facility(
        facility_code="0112345678",
        facility_name="テスト病院",
        prefecture_code="01",
        facility_type=FacilityType.DPC_TARGET,
        bed_count=200,
    )


@pytest.fixture
def sample_ward() -> Ward:
    return Ward(
        facility_code="0112345678",
        ward_code="01",
        ward_name="一般病棟1",
        ward_type=WardType.GENERAL,
        bed_count=50,
        nursing_grade="7対1",
    )


@pytest.fixture
def sample_patient() -> Patient:
    return Patient(
        patient_id="P0001",
        birth_date=date(1960, 5, 15),
        sex=Sex.MALE,
        kana_name="ヤマダ タロウ",
    )


@pytest.fixture
def sample_episode() -> AdmissionEpisode:
    return AdmissionEpisode(
        episode_id="E0001",
        facility_code="0112345678",
        patient_id="P0001",
        admission_date=date(2025, 4, 1),
        discharge_date=date(2025, 4, 10),
        dpc_code="01002xxxe4xx0x",
        main_diagnosis_icd="I500",
        admission_route=AdmissionRoute.EMERGENCY,
        payer_type=PayerType.SOCIAL_INSURANCE,
    )
