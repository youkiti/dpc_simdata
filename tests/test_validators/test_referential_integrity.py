"""参照整合性バリデーターのテスト."""

from pathlib import Path

from dpc_simdata.cli import build_pipeline
from dpc_simdata.generators.registry import GenerationConfig
from dpc_simdata.validators.referential_integrity import validate_cross_file_integrity


class TestReferentialIntegrity:
    def test_generated_data_passes(self, tmp_path: Path) -> None:
        config = GenerationConfig(root_seed=42, output_dir=tmp_path, num_patients=5)
        build_pipeline().run(config)
        errors = validate_cross_file_integrity(tmp_path)
        assert errors == []

    def test_empty_directory_no_errors(self, tmp_path: Path) -> None:
        errors = validate_cross_file_integrity(tmp_path)
        assert errors == []
