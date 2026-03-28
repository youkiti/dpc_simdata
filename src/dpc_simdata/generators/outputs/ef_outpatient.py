"""外来EF統合ファイル 出力ジェネレーター."""

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.facility import FacilityType
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv

# シミュレーション用の外来診療行為プール
_OUTPATIENT_PROCEDURES = [
    ("111000110", "初診料", 291),
    ("112007410", "外来診療料", 74),
    ("120002910", "処方料", 42),
    ("150150810", "生化学的検査判断料", 144),
    ("160006410", "コンピューター断層撮影診断料", 450),
]


def emit_ef_outpatient(ctx: GenerationContext) -> None:
    """外来EF統合ファイルのCSVを出力する.

    外来データは施設種別がDPC対象/準備病院の場合のみ作成する。
    現時点ではシミュレーション用に少数の外来レコードを生成する。
    """
    assert ctx.facility is not None

    if ctx.facility.facility_type not in (FacilityType.DPC_TARGET, FacilityType.DPC_PREP):
        return

    schema = load_schema("ef_outpatient")
    rng = ctx.seed_manager.rng("ef_outpatient")

    ym = ctx.config.target_year_month
    year = int(ym[:4])
    month = int(ym[4:6])

    records: list[dict[str, str]] = []
    seq = 0

    # 患者の一部を外来受診者として扱う
    num_outpatients = max(1, len(ctx.patients) // 3)
    outpatients = rng.sample(ctx.patients, min(num_outpatients, len(ctx.patients)))

    for patient in outpatients:
        visit_day = rng.randint(1, 28)
        visit_date = f"{year}{month:02d}{visit_day:02d}"

        num_items = rng.randint(1, 3)
        selected = rng.sample(_OUTPATIENT_PROCEDURES, min(num_items, len(_OUTPATIENT_PROCEDURES)))

        for code, name, tensu in selected:
            seq += 1
            qty = 1
            records.append({
                "facility_code": ctx.facility.facility_code,
                "year_month": ym,
                "patient_id": patient.patient_id,
                "record_type": "EF",
                "sequence_number": str(seq),
                "shinryo_code": code,
                "shinryo_name": name,
                "tensu": str(tensu),
                "quantity": str(qty),
                "visit_date": visit_date,
            })

    output_path = ctx.config.output_dir / "ef_outpatient.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["ef_outpatient"] = output_path
