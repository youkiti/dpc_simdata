"""生成パイプラインのレジストリとコンテキスト."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from dpc_simdata.generators.seed import SeedManager
from dpc_simdata.models.admission import AdmissionEpisode, TransferEvent
from dpc_simdata.models.clinical import ClaimLine, Diagnosis, Procedure
from dpc_simdata.models.daily import DailyStatus
from dpc_simdata.models.facility import Facility, FacilityType, Ward
from dpc_simdata.models.patient import Patient
from dpc_simdata.models.payer import PayerContext


@dataclass
class GenerationConfig:
    """生成パラメータ."""

    root_seed: int = 42
    target_year_month: str = "202504"
    num_patients: int = 10
    num_wards: int = 3
    output_dir: Path = field(default_factory=lambda: Path("output"))
    facility_type: FacilityType = FacilityType.DPC_TARGET


@dataclass
class GenerationContext:
    """全生成段階で共有される状態コンテナ."""

    config: GenerationConfig
    seed_manager: SeedManager

    # エンティティストア（生成順に設定される）
    facility: Facility | None = None
    wards: list[Ward] = field(default_factory=list)
    patients: list[Patient] = field(default_factory=list)
    episodes: list[AdmissionEpisode] = field(default_factory=list)
    transfers: list[TransferEvent] = field(default_factory=list)
    diagnoses: list[Diagnosis] = field(default_factory=list)
    procedures: list[Procedure] = field(default_factory=list)
    claim_lines: list[ClaimLine] = field(default_factory=list)
    payer_contexts: list[PayerContext] = field(default_factory=list)
    daily_statuses: list[DailyStatus] = field(default_factory=list)

    # 出力ファイルパス
    output_files: dict[str, Path] = field(default_factory=dict)


# ステージ関数の型
StageFunc = Callable[[GenerationContext], None]


class GenerationPipeline:
    """依存順にステージを逐次実行するパイプライン."""

    def __init__(self) -> None:
        self._stages: list[tuple[str, StageFunc]] = []

    def add_stage(self, name: str, func: StageFunc) -> None:
        """ステージを追加する."""
        self._stages.append((name, func))

    def run(self, config: GenerationConfig) -> dict[str, Path]:
        """全ステージを実行し、出力ファイルパスを返す."""
        ctx = GenerationContext(
            config=config,
            seed_manager=SeedManager(config.root_seed),
        )
        for _name, func in self._stages:
            func(ctx)
        return dict(ctx.output_files)
