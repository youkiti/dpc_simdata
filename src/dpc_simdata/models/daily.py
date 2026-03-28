"""日次入院状態の内部モデル定義."""

from datetime import date

from pydantic import BaseModel, Field


class NursingNecessity(BaseModel, frozen=True):
    """看護必要度評価項目."""

    a_score: int = Field(ge=0, le=10, description="A項目スコア")
    b_score: int = Field(ge=0, le=10, description="B項目スコア")
    c_score: int = Field(ge=0, le=3, description="C項目スコア")


class DailyStatus(BaseModel, frozen=True):
    """日次入院状態."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    status_date: date = Field(description="評価日")
    ward_code: str = Field(min_length=1, description="病棟コード")
    nursing_necessity: NursingNecessity = Field(description="看護必要度評価")
