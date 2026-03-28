"""入院EF統合ファイル 出力ジェネレーター."""

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.clinical import ClaimCategory
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv

_CLAIM_CATEGORY_CODE: dict[ClaimCategory, str] = {
    ClaimCategory.FEE_FOR_SERVICE: "01",
    ClaimCategory.INCLUSIVE: "02",
}


def emit_ef_inpatient(ctx: GenerationContext) -> None:
    """入院EF統合ファイルのCSVを出力する."""
    assert ctx.facility is not None
    assert len(ctx.claim_lines) > 0

    schema = load_schema("ef_inpatient")

    ep_map = {ep.episode_id: ep for ep in ctx.episodes}
    records: list[dict[str, str]] = []

    for seq, cl in enumerate(ctx.claim_lines, start=1):
        ep = ep_map[cl.episode_id]
        total_tensu = cl.tensu * cl.quantity

        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": cl.claim_month,
            "patient_id": ep.patient_id,
            "episode_id": cl.episode_id,
            "record_type": "EF",
            "sequence_number": str(seq),
            "shinryo_code": cl.shinryo_code,
            "shinryo_name": cl.shinryo_name,
            "tensu": str(cl.tensu),
            "quantity": str(cl.quantity),
            "total_tensu": str(total_tensu),
            "claim_category": _CLAIM_CATEGORY_CODE.get(cl.category, "99"),
        })

    output_path = ctx.config.output_dir / "ef_inpatient.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["ef_inpatient"] = output_path
