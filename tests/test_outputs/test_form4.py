"""様式4 出力のテスト."""

import csv
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.form4 import emit_form4
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


class TestForm4Output:
    def test_file_created(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form4(ctx)
        assert ctx.output_files["form4"].exists()

    def test_row_count_matches_episodes(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form4(ctx)
        with ctx.output_files["form4"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        # form4はform1と同じ症例＋医科保険以外を含む（現時点では全症例が対象）
        assert len(rows) == len(ctx.episodes)

    def test_column_count(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form4(ctx)
        with ctx.output_files["form4"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert len(row) == 10

    def test_flags_are_binary(self, tmp_path: Path) -> None:
        ctx = _build_context(tmp_path)
        emit_form4(ctx)
        with ctx.output_files["form4"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        for row in rows:
            assert row[7] in ("0", "1")  # has_non_medical_insurance
            assert row[8] in ("0", "1")  # self_pay_flag
            assert row[9] in ("0", "1")  # workers_comp_flag

    def test_form4_superset_of_form1_episodes(self, tmp_path: Path) -> None:
        """form4の対象症例はform1の対象をスーパーセットとして含む."""
        ctx = _build_context(tmp_path)
        emit_form4(ctx)
        with ctx.output_files["form4"].open(encoding="shift_jis") as f:
            rows = list(csv.reader(f))
        form4_episode_ids = {row[3] for row in rows}
        form1_episode_ids = {ep.episode_id for ep in ctx.episodes}
        assert form1_episode_ids.issubset(form4_episode_ids)
