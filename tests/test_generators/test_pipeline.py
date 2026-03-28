"""パイプライン統合テスト."""

from pathlib import Path

from dpc_simdata.cli import build_pipeline
from dpc_simdata.generators.registry import GenerationConfig
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.validators.referential_integrity import validate_cross_file_integrity
from dpc_simdata.validators.schema_validator import validate_output


class TestPipelineIntegration:
    def test_full_pipeline_produces_all_files(self, tmp_path: Path) -> None:
        config = GenerationConfig(root_seed=42, output_dir=tmp_path, num_patients=5)
        pipeline = build_pipeline()
        output_files = pipeline.run(config)

        expected = {"form1", "form3", "form4", "ef_inpatient", "d_file", "h_file", "ef_outpatient", "k_file"}
        assert set(output_files.keys()) == expected
        for path in output_files.values():
            assert path.exists()
            assert path.stat().st_size > 0

    def test_referential_integrity_passes(self, tmp_path: Path) -> None:
        config = GenerationConfig(root_seed=42, output_dir=tmp_path, num_patients=5)
        pipeline = build_pipeline()
        pipeline.run(config)

        errors = validate_cross_file_integrity(tmp_path)
        assert errors == [], f"整合性エラー: {errors}"

    def test_schema_validation_passes_for_all_files(self, tmp_path: Path) -> None:
        config = GenerationConfig(root_seed=42, output_dir=tmp_path, num_patients=5)
        pipeline = build_pipeline()
        output_files = pipeline.run(config)

        for name, path in output_files.items():
            schema = load_schema(name)
            errors = validate_output(path, schema)
            assert errors == [], f"{name}のスキーマ検証エラー: {errors}"

    def test_reproducibility(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"

        config1 = GenerationConfig(root_seed=42, output_dir=dir1, num_patients=5)
        config2 = GenerationConfig(root_seed=42, output_dir=dir2, num_patients=5)

        pipeline1 = build_pipeline()
        pipeline2 = build_pipeline()

        files1 = pipeline1.run(config1)
        files2 = pipeline2.run(config2)

        for name in files1:
            content1 = files1[name].read_bytes()
            content2 = files2[name].read_bytes()
            assert content1 == content2, f"{name}の出力が一致しません"

    def test_different_seed_different_output(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "seed42"
        dir2 = tmp_path / "seed99"

        config1 = GenerationConfig(root_seed=42, output_dir=dir1, num_patients=5)
        config2 = GenerationConfig(root_seed=99, output_dir=dir2, num_patients=5)

        files1 = build_pipeline().run(config1)
        files2 = build_pipeline().run(config2)

        assert files1["form1"].read_bytes() != files2["form1"].read_bytes()
