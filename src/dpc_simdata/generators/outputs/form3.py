"""様式3 出力ジェネレーター."""

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.facility import FacilityType, WardType
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv

# 内部Enum値 → 出力コード値のマッピング
_FACILITY_TYPE_CODE: dict[FacilityType, str] = {
    FacilityType.DPC_TARGET: "01",
    FacilityType.DPC_PREP: "02",
    FacilityType.FEE_FOR_SERVICE: "03",
}

_WARD_TYPE_CODE: dict[WardType, str] = {
    WardType.GENERAL: "01",
    WardType.SPECIFIC: "02",
    WardType.ICU: "03",
    WardType.HCU: "04",
    WardType.NICU: "05",
    WardType.PSYCHIATRIC: "06",
    WardType.REHABILITATION: "07",
}


def emit_form3(ctx: GenerationContext) -> None:
    """様式3のCSVファイルを出力する."""
    assert ctx.facility is not None, "facility must be generated before form3"
    assert len(ctx.wards) > 0, "wards must be generated before form3"

    schema = load_schema("form3")
    records: list[dict[str, str]] = []

    for ward in ctx.wards:
        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": ctx.config.target_year_month,
            "ward_code": ward.ward_code,
            "ward_name": ward.ward_name,
            "bed_count": str(ward.bed_count),
            "ward_type": _WARD_TYPE_CODE.get(ward.ward_type, "99"),
            "nursing_grade": ward.nursing_grade,
            "facility_type": _FACILITY_TYPE_CODE.get(ctx.facility.facility_type, "99"),
            "total_bed_count": str(ctx.facility.bed_count),
            "prefecture_code": ctx.facility.prefecture_code,
        })

    output_path = ctx.config.output_dir / "form3.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["form3"] = output_path
