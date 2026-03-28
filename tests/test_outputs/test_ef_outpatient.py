"""外来EF統合ファイル 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.ef_outpatient import emit_ef_outpatient
from dpc_simdata.generators.patients import generate_patients
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager
from dpc_simdata.models.facility import FacilityType


def _build_context(
    tmp_path: Path, seed: int = 42, facility_type: FacilityType = FacilityType.DPC_TARGET
) -> GenerationContext:
    config = GenerationConfig(root_seed=seed, output_dir=tmp_path, num_patients=5, facility_type=facility_type)
    ctx = GenerationContext(config=config, seed_manager=SeedManager(seed))
    generate_facility(ctx)
    generate_patients(ctx)
    generate_episodes(ctx)
    generate_clinical(ctx)
    return ctx


class TestEfOutpatientOutput:
    def test_file_created_for_dpc(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_ef_outpatient(ctx)
        assert ctx.output_files["ef_outpatient"].exists()

    def test_no_file_for_fee_for_service(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path, facility_type=FacilityType.FEE_FOR_SERVICE)
        emit_ef_outpatient(ctx)
        assert "ef_outpatient" not in ctx.output_files

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_ef_outpatient(ctx)
        with ctx.output_files["ef_outpatient"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 10

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_ef_outpatient(ctx1)
        emit_ef_outpatient(ctx2)
        assert ctx1.output_files["ef_outpatient"].read_bytes() == ctx2.output_files["ef_outpatient"].read_bytes()
