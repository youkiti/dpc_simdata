"""支払情報の内部モデル定義."""

from pydantic import BaseModel, Field

from dpc_simdata.models.admission import PayerType


class PayerContext(BaseModel, frozen=True):
    """支払コンテキスト."""

    episode_id: str = Field(min_length=1, description="入院エピソードID")
    payer_type: PayerType = Field(description="支払区分")
    insurer_number: str | None = Field(default=None, description="保険者番号")
    public_expense_code: str | None = Field(default=None, description="公費負担者番号")
