"""Dファイル 出力ジェネレーター."""

from dpc_simdata.generators.outputs.form1 import _format_date
from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.facility import FacilityType
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv

# シミュレーション用の医療機関別係数
_DEFAULT_COEFFICIENT = "1.0500"
# シミュレーション用の包括日額点数
_DEFAULT_INCLUSIVE_TENSU = 2000


def emit_d_file(ctx: GenerationContext) -> None:
    """DファイルのCSVを出力する（DPC対象病院のみ）."""
    assert ctx.facility is not None

    if ctx.facility.facility_type != FacilityType.DPC_TARGET:
        return

    schema = load_schema("d_file")
    records: list[dict[str, str]] = []

    for ep in ctx.episodes:
        if not ep.dpc_code:
            continue

        los = (ep.discharge_date - ep.admission_date).days if ep.discharge_date else 0
        claim_month = f"{ep.admission_date.year}{ep.admission_date.month:02d}"
        total_inclusive = _DEFAULT_INCLUSIVE_TENSU * los

        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": claim_month,
            "patient_id": ep.patient_id,
            "episode_id": ep.episode_id,
            "dpc_code": ep.dpc_code,
            "admission_date": _format_date(ep.admission_date),
            "discharge_date": _format_date(ep.discharge_date) if ep.discharge_date else "",
            "inclusive_tensu": str(_DEFAULT_INCLUSIVE_TENSU),
            "los_days": str(los),
            "medical_institution_coefficient": _DEFAULT_COEFFICIENT,
            "fee_for_service_reason": "",
            "total_inclusive_tensu": str(total_inclusive),
        })

    output_path = ctx.config.output_dir / "d_file.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["d_file"] = output_path
