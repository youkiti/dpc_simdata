"""入院EF統合ファイル 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.ef_inpatient import emit_ef_inpatient
from dpc_simdata.generators.patients import generate_patients
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager


def _build_context(tmp_path: Path, seed: int = 42) -> GenerationContext:
    config = GenerationConfig(root_seed=seed, output_dir=tmp_path, num_patients=5)
    ctx = GenerationContext(config=config, seed_manager=SeedManager(seed))
    generate_facility(ctx)
    generate_patients(ctx)
    generate_episodes(ctx)
    generate_clinical(ctx)
    return ctx


class TestEfInpatientOutput:
    def test_file_created(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_ef_inpatient(ctx)
        assert ctx.output_files["ef_inpatient"].exists()

    def test_row_count_matches_claim_lines(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_ef_inpatient(ctx)
        with ctx.output_files["ef_inpatient"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        assert len(rows) == len(ctx.claim_lines)

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_ef_inpatient(ctx)
        with ctx.output_files["ef_inpatient"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 12

    def test_episode_ids_subset_of_form1(self, tmp_path: Path) -> None:
        """EF統合ファイルのエピソードIDはform1の対象に含まれる."""
        ctx = _build_context(tmp_path)
        emit_ef_inpatient(ctx)
        with ctx.output_files["ef_inpatient"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        ef_episode_ids = {row[3] for row in rows}
        form1_episode_ids = {ep.episode_id for ep in ctx.episodes}
        assert ef_episode_ids.issubset(form1_episode_ids)

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_ef_inpatient(ctx1)
        emit_ef_inpatient(ctx2)
        assert ctx1.output_files["ef_inpatient"].read_bytes() == ctx2.output_files["ef_inpatient"].read_bytes()
