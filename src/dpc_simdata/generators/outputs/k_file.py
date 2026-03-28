"""Kファイル 出力ジェネレーター."""

import hashlib

from dpc_simdata.generators.outputs.form1 import _format_date
from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv


def _generate_dummy_common_id(birth_date_str: str, sex: str, kana_name: str) -> str:
    """一次共通IDのダミー値を生成する.

    実際は支援ツール依存のため、SHA256ハッシュで代替する。
    """
    data = f"{birth_date_str}:{sex}:{kana_name}".encode()
    return hashlib.sha256(data).hexdigest()


def emit_k_file(ctx: GenerationContext) -> None:
    """Kファイル（一次共通ID）のCSVを出力する.

    対象: ef_inpatientに含まれる症例の患者に限る。
    """
    assert ctx.facility is not None

    schema = load_schema("k_file")

    # ef_inpatient対象の患者IDを特定
    ef_patient_ids = {ep.patient_id for ep in ctx.episodes}
    patient_map = {p.patient_id: p for p in ctx.patients}

    records: list[dict[str, str]] = []
    seen_patients: set[str] = set()

    for patient_id in ef_patient_ids:
        if patient_id in seen_patients:
            continue
        seen_patients.add(patient_id)

        patient = patient_map[patient_id]
        birth_str = _format_date(patient.birth_date)
        common_id = _generate_dummy_common_id(birth_str, patient.sex.value, patient.kana_name)

        records.append({
            "facility_code": ctx.facility.facility_code,
            "year_month": ctx.config.target_year_month,
            "patient_id": patient.patient_id,
            "birth_date": birth_str,
            "sex": patient.sex.value,
            "kana_name": patient.kana_name,
            "primary_common_id": common_id,
        })

    output_path = ctx.config.output_dir / "k_file.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["k_file"] = output_path
