"""診断・処置・請求明細の内部モデル定義."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class DiagnosisCategory(StrEnum):
    """診断区分."""

    MAIN = "main"  # 主傷病
    SECONDARY = "secondary"  # 副傷病
    TRIGGER = "trigger"  # 入院の契機となった傷病
    COMORBIDITY = "comorbidity"  # 併存症
    COMPLICATION = "complication"  # 続発症


class ClaimCategory(StrEnum):
    """請求区分."""

    FEE_FOR_SERVICE = "fee_for_service"  # 出来高
    INCLUSIVE = "inclusive"  # 包括


class Diagnosis(BaseModel, frozen=True):
    """診断."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    icd_code: str = Field(min_length=3, description="ICDコード")
    diagnosis_category: DiagnosisCategory = Field(description="診断区分")
    diagnosis_name: str = Field(min_length=1, description="傷病名")
    onset_date: date | None = Field(default=None, description="発症日")


class Procedure(BaseModel, frozen=True):
    """処置・手術."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    procedure_code: str = Field(min_length=1, description="診療行為コード（Kコード等）")
    procedure_name: str = Field(min_length=1, description="診療行為名称")
    procedure_date: date = Field(description="実施日")
    quantity: int = Field(ge=1, default=1, description="回数")


class ClaimLine(BaseModel, frozen=True):
    """請求明細行."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    claim_month: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$", description="請求年月（YYYYMM）")
    shinryo_code: str = Field(min_length=1, description="診療行為コード")
    shinryo_name: str = Field(min_length=1, description="診療行為名称")
    tensu: int = Field(ge=0, description="点数")
    quantity: int = Field(ge=1, default=1, description="回数")
    category: ClaimCategory = Field(description="請求区分")
