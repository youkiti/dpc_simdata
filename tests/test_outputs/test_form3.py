"""様式3 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.form3 import emit_form3
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager


class TestForm3Output:
    def _run_form3(self, tmp_path: Path, seed: int = 42) -> GenerationContext:
        config = GenerationConfig(root_seed=seed, output_dir=tmp_path, num_wards=3)
        ctx = GenerationContext(config=config, seed_manager=SeedManager(seed))
        generate_facility(ctx)
        emit_form3(ctx)
        return ctx

    def test_file_created(self, tmp_path: Path) -> None:
        ctx = self._run_form3(tmp_path)
        assert ctx.output_files["form3"].exists()

    def test_row_count_matches_wards(self, tmp_path: Path) -> None:
        ctx = self._run_form3(tmp_path)
        with ctx.output_files["form3"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 3  # 3病棟 = 3行

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = self._run_form3(tmp_path)
        with ctx.output_files["form3"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 10

    def test_facility_code_consistent(self, tmp_path: Path) -> None:
        ctx = self._run_form3(tmp_path)
        with ctx.output_files["form3"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert row[0] == ctx.facility.facility_code

    def test_year_month(self, tmp_path: Path) -> None:
        ctx = self._run_form3(tmp_path)
        with ctx.output_files["form3"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert row[1] == "202504"

    def test_reproducible(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        ctx1 = self._run_form3(dir1, seed=42)
        ctx2 = self._run_form3(dir2, seed=42)
        content1 = ctx1.output_files["form3"].read_bytes()
        content2 = ctx2.output_files["form3"].read_bytes()
        assert content1 == content2
