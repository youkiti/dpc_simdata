"""Kファイル 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.k_file import emit_k_file
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


class TestKFileOutput:
    def test_file_created(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_k_file(ctx)
        assert ctx.output_files["k_file"].exists()

    def test_patients_subset_of_ef_inpatient(self, tmp_path: Path) -> None:
        """k_fileの患者はef_inpatient対象の症例に限る."""
        ctx = _build_context(tmp_path)
        emit_k_file(ctx)
        with ctx.output_files["k_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        k_patient_ids = {row[2] for row in rows}
        ef_patient_ids = {ep.patient_id for ep in ctx.episodes}
        assert k_patient_ids.issubset(ef_patient_ids)

    def test_no_duplicate_patients(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_k_file(ctx)
        with ctx.output_files["k_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        patient_ids = [row[2] for row in rows]
        assert len(patient_ids) == len(set(patient_ids))

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_k_file(ctx)
        with ctx.output_files["k_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 7

    def test_common_id_is_64_chars(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_k_file(ctx)
        with ctx.output_files["k_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row[6]) == 64  # SHA256 hex digest

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_k_file(ctx1)
        emit_k_file(ctx2)
        assert ctx1.output_files["k_file"].read_bytes() == ctx2.output_files["k_file"].read_bytes()
