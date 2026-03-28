"""DPC SimData CLI エントリポイント."""

import argparse
import sys
from pathlib import Path

from dpc_simdata.generators.clinical import generate_clinical
from dpc_simdata.generators.episodes import generate_episodes
from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.outputs.d_file import emit_d_file
from dpc_simdata.generators.outputs.ef_inpatient import emit_ef_inpatient
from dpc_simdata.generators.outputs.ef_outpatient import emit_ef_outpatient
from dpc_simdata.generators.outputs.form1 import emit_form1
from dpc_simdata.generators.outputs.form3 import emit_form3
from dpc_simdata.generators.outputs.form4 import emit_form4
from dpc_simdata.generators.outputs.h_file import emit_h_file
from dpc_simdata.generators.outputs.k_file import emit_k_file
from dpc_simdata.generators.patients import generate_patients
from dpc_simdata.generators.registry import GenerationConfig, GenerationPipeline
from dpc_simdata.models.facility import FacilityType
from dpc_simdata.validators.referential_integrity import validate_cross_file_integrity


def build_pipeline() -> GenerationPipeline:
    """標準パイプラインを構築する."""
    pipeline = GenerationPipeline()
    pipeline.add_stage("facility", generate_facility)
    pipeline.add_stage("patients", generate_patients)
    pipeline.add_stage("episodes", generate_episodes)
    pipeline.add_stage("clinical", generate_clinical)
    pipeline.add_stage("form3", emit_form3)
    pipeline.add_stage("form1", emit_form1)
    pipeline.add_stage("form4", emit_form4)
    pipeline.add_stage("ef_inpatient", emit_ef_inpatient)
    pipeline.add_stage("d_file", emit_d_file)
    pipeline.add_stage("h_file", emit_h_file)
    pipeline.add_stage("ef_outpatient", emit_ef_outpatient)
    pipeline.add_stage("k_file", emit_k_file)
    return pipeline


def main(argv: list[str] | None = None) -> int:
    """CLIメイン関数."""
    parser = argparse.ArgumentParser(description="DPC提出データのシミュレーションデータを生成する")
    parser.add_argument("--seed", type=int, default=42, help="ルートシード（デフォルト: 42）")
    parser.add_argument("--year-month", type=str, default="202504", help="対象年月（YYYYMM、デフォルト: 202504）")
    parser.add_argument("--num-patients", type=int, default=10, help="患者数（デフォルト: 10）")
    parser.add_argument("--num-wards", type=int, default=3, help="病棟数（デフォルト: 3）")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="出力先ディレクトリ")
    parser.add_argument(
        "--facility-type",
        type=str,
        choices=["dpc_target", "dpc_prep", "fee_for_service"],
        default="dpc_target",
        help="施設種別",
    )
    parser.add_argument("--admission-start", type=str, default="", help="入院期間の開始年月（YYYYMM）")
    parser.add_argument("--admission-end", type=str, default="", help="入院期間の終了年月（YYYYMM）")
    parser.add_argument("--validate", action="store_true", help="生成後に参照整合性を検証する")

    args = parser.parse_args(argv)

    config = GenerationConfig(
        root_seed=args.seed,
        target_year_month=args.year_month,
        num_patients=args.num_patients,
        num_wards=args.num_wards,
        output_dir=args.output_dir,
        facility_type=FacilityType(args.facility_type),
        admission_start=args.admission_start,
        admission_end=args.admission_end,
    )

    pipeline = build_pipeline()
    output_files = pipeline.run(config)

    print(f"生成完了: {len(output_files)} ファイル")
    for name, path in sorted(output_files.items()):
        print(f"  {name}: {path}")

    if args.validate:
        errors = validate_cross_file_integrity(args.output_dir)
        if errors:
            print(f"\n参照整合性エラー: {len(errors)} 件")
            for err in errors:
                print(f"  [{err.check}] {err.message}")
            return 1
        print("\n参照整合性検証: OK")

    return 0


if __name__ == "__main__":
    sys.exit(main())
