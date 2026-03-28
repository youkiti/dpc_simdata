"""患者の内部モデル定義."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Sex(StrEnum):
    """性別."""

    MALE = "1"
    FEMALE = "2"


class Patient(BaseModel, frozen=True):
    """患者."""

    patient_id: str = Field(min_length=1, description="匿名化患者ID（調査期間を通じて一貫）")
    birth_date: date = Field(description="生年月日")
    sex: Sex = Field(description="性別")
    kana_name: str = Field(min_length=1, description="カナ氏名（k_file用）")
    postal_code: str | None = Field(default=None, pattern=r"^\d{7}$", description="郵便番号（7桁、ハイフンなし）")
