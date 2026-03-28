"""Hファイル 出力ジェネレーター."""

from dpc_simdata.generators.outputs.form1 import _format_date
from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv


def emit_h_file(ctx: GenerationContext) -> None:
    """Hファイル（看護必要度日次評価）のCSVを出力する."""
    assert ctx.facility is not None

    schema = load_schema("h_file")
    ep_map = {ep.episode_id: ep for ep in ctx.episodes}
    records: list[dict[str, str]] = []

    for ds in ctx.daily_statuses:
        ep = ep_map[ds.episode_id]
        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": ctx.config.target_year_month,
            "patient_id": ep.patient_id,
            "episode_id": ds.episode_id,
            "status_date": _format_date(ds.status_date),
            "ward_code": ds.ward_code,
            "a_score": str(ds.nursing_necessity.a_score),
            "b_score": str(ds.nursing_necessity.b_score),
            "c_score": str(ds.nursing_necessity.c_score),
        })

    output_path = ctx.config.output_dir / "h_file.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["h_file"] = output_path
