"""Hファイル 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.h_file import emit_h_file
from dpc_simdata.generators.patients import generate_patients
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager


def _build_context(tmp_path: Path, seed: int = 42) -> GenerationContext:
    config = GenerationConfig(root_seed=seed, output_dir=tmp_path, num_patients=3)
    ctx = GenerationContext(config=config, seed_manager=SeedManager(seed))
    generate_facility(ctx)
    generate_patients(ctx)
    generate_episodes(ctx)
    generate_clinical(ctx)
    return ctx


class TestHFileOutput:
    def test_file_created(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_h_file(ctx)
        assert ctx.output_files["h_file"].exists()

    def test_row_count_matches_daily_statuses(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_h_file(ctx)
        with ctx.output_files["h_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        assert len(rows) == len(ctx.daily_statuses)

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_h_file(ctx)
        with ctx.output_files["h_file"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 9

    def test_date_range_matches_form1(self, tmp_path: Path) -> None:
        """h_fileの日付範囲がform1の入退院期間と一致する."""
        ctx = _build_context(tmp_path)
        emit_h_file(ctx)

        for ep in ctx.episodes:
            ep_dailies = [ds for ds in ctx.daily_statuses if ds.episode_id == ep.episode_id]
            if ep.discharge_date and ep_dailies:
                dates = sorted(ds.status_date for ds in ep_dailies)
                assert dates[0] == ep.admission_date
                assert dates[-1] < ep.discharge_date

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = _build_context(dir1)
        ctx2 = _build_context(dir2)
        emit_h_file(ctx1)
        emit_h_file(ctx2)
        assert ctx1.output_files["h_file"].read_bytes() == ctx2.output_files["h_file"].read_bytes()
