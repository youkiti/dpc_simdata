"""入院エピソード・転棟イベントの内部モデル定義."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class AdmissionRoute(StrEnum):
    """入院経路."""

    EMERGENCY = "emergency"
    ELECTIVE = "elective"
    TRANSFER_IN = "transfer_in"
    OTHER = "other"


class DischargeStatus(StrEnum):
    """退院先."""

    HOME = "home"
    TRANSFER_OUT = "transfer_out"
    DEATH = "death"
    OTHER = "other"


class PayerType(StrEnum):
    """支払区分."""

    SOCIAL_INSURANCE = "social_insurance"  # 社保
    NATIONAL_INSURANCE = "national_insurance"  # 国保
    LATE_ELDERLY = "late_elderly"  # 後期高齢
    PUBLIC_EXPENSE = "public_expense"  # 公費
    WORKERS_COMP = "workers_comp"  # 労災
    SELF_PAY = "self_pay"  # 自費
    OTHER = "other"


class TransferReason(StrEnum):
    """転棟理由."""

    CLINICAL = "clinical"
    BED_MANAGEMENT = "bed_management"
    OTHER = "other"


class AdmissionEpisode(BaseModel, frozen=True):
    """入院エピソード."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    facility_code: str = Field(min_length=10, max_length=10, description="医療機関コード")
    patient_id: str = Field(min_length=1, description="患者ID")
    admission_date: date = Field(description="入院日")
    discharge_date: date | None = Field(default=None, description="退院日（入院中はNone）")
    discharge_status: DischargeStatus | None = Field(default=None, description="退院先")
    dpc_code: str | None = Field(default=None, min_length=14, max_length=14, description="DPCコード（14桁）")
    main_diagnosis_icd: str = Field(min_length=3, description="主傷病ICDコード")
    admission_route: AdmissionRoute = Field(description="入院経路")
    payer_type: PayerType = Field(description="支払区分")


class TransferEvent(BaseModel, frozen=True):
    """転棟イベント."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    transfer_date: date = Field(description="転棟日")
    from_ward_code: str = Field(min_length=1, description="転棟元病棟コード")
    to_ward_code: str = Field(min_length=1, description="転棟先病棟コード")
    reason: TransferReason = Field(description="転棟理由")
