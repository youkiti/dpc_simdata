"""AdmissionEpisode / TransferEvent モデルのテスト."""

from datetime import date

import pytest
from pydantic import ValidationError

from dpc_simdata.models.admission import (
    AdmissionEpisode,
    AdmissionRoute,
    PayerType,
    TransferEvent,
    TransferReason,
)


class TestAdmissionEpisode:
    def test_valid_episode(self, sample_episode: AdmissionEpisode) -> None:
        assert sample_episode.episode_id == "E0001"
        assert sample_episode.dpc_code == "01002xxxe4xx0x"
        assert len(sample_episode.dpc_code) == 14

    def test_episode_without_discharge(self) -> None:
        ep = AdmissionEpisode(
            episode_id="E0002",
            facility_code="0112345678",
            patient_id="P0001",
            admission_date=date(2025, 4, 1),
            main_diagnosis_icd="I500",
            admission_route=AdmissionRoute.ELECTIVE,
            payer_type=PayerType.NATIONAL_INSURANCE,
        )
        assert ep.discharge_date is None
        assert ep.discharge_status is None

    def test_dpc_code_must_be_14_chars(self) -> None:
        with pytest.raises(ValidationError):
            AdmissionEpisode(
                episode_id="E0003",
                facility_code="0112345678",
                patient_id="P0001",
                admission_date=date(2025, 4, 1),
                dpc_code="0100",
                main_diagnosis_icd="I500",
                admission_route=AdmissionRoute.EMERGENCY,
                payer_type=PayerType.SOCIAL_INSURANCE,
            )


class TestTransferEvent:
    def test_valid_transfer(self) -> None:
        t = TransferEvent(
            episode_id="E0001",
            transfer_date=date(2025, 4, 5),
            from_ward_code="01",
            to_ward_code="02",
            reason=TransferReason.CLINICAL,
        )
        assert t.from_ward_code == "01"
        assert t.to_ward_code == "02"
