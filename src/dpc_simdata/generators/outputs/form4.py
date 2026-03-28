"""様式4 出力ジェネレーター."""

from dpc_simdata.generators.outputs.form1 import _PAYER_TYPE_CODE, _format_date
from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.admission import PayerType
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv


def emit_form4(ctx: GenerationContext) -> None:
    """様式4のCSVファイルを出力する.

    form4はform1の対象症例に加え、医科保険以��（自費、労災等）の入院も対象に含む。
    """
    assert ctx.facility is not None
    assert len(ctx.episodes) > 0

    schema = load_schema("form4")
    records: list[dict[str, str]] = []

    for ep in ctx.episodes:
        is_self_pay = ep.payer_type == PayerType.SELF_PAY
        is_workers_comp = ep.payer_type == PayerType.WORKERS_COMP
        has_non_medical = is_self_pay or is_workers_comp

        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": ctx.config.target_year_month,
            "patient_id": ep.patient_id,
            "episode_id": ep.episode_id,
            "admission_date": _format_date(ep.admission_date),
            "discharge_date": _format_date(ep.discharge_date) if ep.discharge_date else "",
            "payer_type": _PAYER_TYPE_CODE.get(ep.payer_type, "99"),
            "has_non_medical_insurance": "1" if has_non_medical else "0",
            "self_pay_flag": "1" if is_self_pay else "0",
            "workers_comp_flag": "1" if is_workers_comp else "0",
        })

    output_path = ctx.config.output_dir / "form4.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["form4"] = output_path
