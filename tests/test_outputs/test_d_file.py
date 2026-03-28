"""Dファイル 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.d_file import emit_d_file
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


class TestDFileOutput:
    def test_file_created_for_dpc_target(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_d_file(ctx)
        assert ctx.output_files["d_file"].exists()

    def test_no_file_for_non_dpc(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path, facility_type=FacilityType.FEE_FOR_SERVICE)
        emit_d_file(ctx)
        assert "d_file" not in ctx.output_files

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_d_file(ctx)
        with ctx.output_files["d_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 12

    def test_dpc_code_present(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_d_file(ctx)
        with ctx.output_files["d_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row[4]) == 14  # DPCコード14桁

    def test_episode_ids_subset_of_form1(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_d_file(ctx)
        with ctx.output_files["d_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        d_episode_ids = {row[3] for row in rows}
        form1_episode_ids = {ep.episode_id for ep in ctx.episodes}
        assert d_episode_ids.issubset(form1_episode_ids)

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_d_file(ctx1)
        emit_d_file(ctx2)
        assert ctx1.output_files["d_file"].read_bytes() == ctx2.output_files["d_file"].read_bytes()
