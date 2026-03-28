"""様式1 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.form1 import emit_form1
from dpc_simdata.generators.patients import generate_patients
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager


def _build_context(tmp_path: Path, seed: int = 42, num_patients: int = 5) -> GenerationContext:
    config = GenerationConfig(root_seed=seed, output_dir=tmp_path, num_patients=num_patients)
    ctx = GenerationContext(config=config, seed_manager=SeedManager(seed))
    generate_facility(ctx)
    generate_patients(ctx)
    generate_episodes(ctx)
    generate_clinical(ctx)
    return ctx


class TestForm1Output:
    def test_file_created(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form1(ctx)
        assert ctx.output_files["form1"].exists()

    def test_row_count_matches_episodes(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form1(ctx)
        with ctx.output_files["form1"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        assert len(rows) == len(ctx.episodes)

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form1(ctx)
        with ctx.output_files["form1"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 30

    def test_facility_code_consistent(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form1(ctx)
        with ctx.output_files["form1"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert row[0] == ctx.facility.facility_code

    def test_patient_ids_match(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form1(ctx)
        with ctx.output_files["form1"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        expected_ids = {ep.patient_id for ep in ctx.episodes}
        actual_ids = {row[2] for row in rows}
        assert actual_ids == expected_ids

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_form1(ctx1)
        emit_form1(ctx2)
        assert ctx1.output_files["form1"].read_bytes() == ctx2.output_files["form1"].read_bytes()
