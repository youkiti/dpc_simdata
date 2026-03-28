"""施設・病棟の内部モデル定義."""

from enum import StrEnum

from pydantic import BaseModel, Field


class FacilityType(StrEnum):
    """施設種別."""

    DPC_TARGET = "dpc_target"  # DPC対象病院
    DPC_PREP = "dpc_prep"  # DPC準備病院
    FEE_FOR_SERVICE = "fee_for_service"  # 出来高病院


class WardType(StrEnum):
    """病棟種別."""

    GENERAL = "general"
    SPECIFIC = "specific"
    ICU = "icu"
    HCU = "hcu"
    NICU = "nicu"
    PSYCHIATRIC = "psychiatric"
    REHABILITATION = "rehabilitation"


class Facility(BaseModel, frozen=True):
    """医療機関."""

    facility_code: str = Field(min_length=10, max_length=10, description="医療機関コード（10桁）")
    facility_name: str = Field(min_length=1, description="医療機関名称")
    prefecture_code: str = Field(min_length=2, max_length=2, pattern=r"^\d{2}$", description="都道府県コード（2桁）")
    facility_type: FacilityType = Field(description="施設種別")
    bed_count: int = Field(ge=1, description="総病床数")


class Ward(BaseModel, frozen=True):
    """病棟."""

    facility_code: str = Field(min_length=10, max_length=10, description="所属施設コード")
    ward_code: str = Field(min_length=1, description="病棟コード")
    ward_name: str = Field(min_length=1, description="病棟名称")
    ward_type: WardType = Field(description="病棟種別")
    bed_count: int = Field(ge=1, description="病床数")
    nursing_grade: str = Field(min_length=1, description="入院基本料等の区分")
