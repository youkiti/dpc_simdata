"""様式1 出力ジェネレーター."""

from datetime import date

from dpc_simdata.generators.outputs.form3 import _FACILITY_TYPE_CODE
from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.admission import AdmissionRoute, DischargeStatus, PayerType
from dpc_simdata.models.clinical import DiagnosisCategory
from dpc_simdata.schemas.loader import load_schema
from dpc_simdata.serializers.csv_writer import serialize_csv

_DISCHARGE_STATUS_CODE: dict[DischargeStatus, str] = {
    DischargeStatus.HOME: "01",
    DischargeStatus.TRANSFER_OUT: "02",
    DischargeStatus.DEATH: "03",
    DischargeStatus.OTHER: "99",
}

_ADMISSION_ROUTE_CODE: dict[AdmissionRoute, str] = {
    AdmissionRoute.EMERGENCY: "01",
    AdmissionRoute.ELECTIVE: "02",
    AdmissionRoute.TRANSFER_IN: "03",
    AdmissionRoute.OTHER: "99",
}

_PAYER_TYPE_CODE: dict[PayerType, str] = {
    PayerType.SOCIAL_INSURANCE: "01",
    PayerType.NATIONAL_INSURANCE: "02",
    PayerType.LATE_ELDERLY: "03",
    PayerType.PUBLIC_EXPENSE: "04",
    PayerType.WORKERS_COMP: "05",
    PayerType.SELF_PAY: "06",
    PayerType.OTHER: "99",
}


def _calc_age(birth_date: date, ref_date: date) -> int:
    age = ref_date.year - birth_date.year
    if (ref_date.month, ref_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def _format_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def emit_form1(ctx: GenerationContext) -> None:
    """様式1のCSVファイルを出力する."""
    assert ctx.facility is not None
    assert len(ctx.episodes) > 0

    schema = load_schema("form1")

    # インデックス構築
    patient_map = {p.patient_id: p for p in ctx.patients}
    diag_by_ep = {}
    for d in ctx.diagnoses:
        diag_by_ep.setdefault(d.episode_id, []).append(d)
    proc_by_ep = {}
    for p in ctx.procedures:
        proc_by_ep.setdefault(p.episode_id, []).append(p)
    transfer_count = {}
    for t in ctx.transfers:
        transfer_count[t.episode_id] = transfer_count.get(t.episode_id, 0) + 1
    payer_map = {pc.episode_id: pc for pc in ctx.payer_contexts}

    records: list[dict[str, str]] = []

    for ep in ctx.episodes:
        patient = patient_map[ep.patient_id]
        ep_diags = diag_by_ep.get(ep.episode_id, [])
        ep_procs = proc_by_ep.get(ep.episode_id, [])
        payer = payer_map.get(ep.episode_id)

        # 主傷病
        main_diag = next((d for d in ep_diags if d.diagnosis_category == DiagnosisCategory.MAIN), None)
        trigger_diag = next((d for d in ep_diags if d.diagnosis_category == DiagnosisCategory.TRIGGER), None)
        secondary_diags = [d for d in ep_diags if d.diagnosis_category == DiagnosisCategory.SECONDARY]

        # 入院時病棟: 転棟がなければwards[0]
        ward_code = ctx.wards[0].ward_code if ctx.wards else ""

        los = (ep.discharge_date - ep.admission_date).days if ep.discharge_date else 0

        record: dict[str, str] = {
            "facility_code": ctx.facility.facility_code,
            "year_month": ctx.config.target_year_month,
            "patient_id": ep.patient_id,
            "episode_id": ep.episode_id,
            "sex": patient.sex.value,
            "birth_date": _format_date(patient.birth_date),
            "postal_code": patient.postal_code or "",
            "admission_date": _format_date(ep.admission_date),
            "discharge_date": _format_date(ep.discharge_date) if ep.discharge_date else "",
            "discharge_status": _DISCHARGE_STATUS_CODE.get(ep.discharge_status, "99") if ep.discharge_status else "",
            "admission_route": _ADMISSION_ROUTE_CODE.get(ep.admission_route, "99"),
            "payer_type": _PAYER_TYPE_CODE.get(ep.payer_type, "99"),
            "dpc_code": ep.dpc_code or "",
            "main_diagnosis_icd": ep.main_diagnosis_icd,
            "main_diagnosis_name": main_diag.diagnosis_name if main_diag else "",
            "trigger_icd": trigger_diag.icd_code if trigger_diag else ep.main_diagnosis_icd,
            "trigger_diagnosis_name": trigger_diag.diagnosis_name if trigger_diag else "",
            "secondary_diagnosis_1_icd": secondary_diags[0].icd_code if secondary_diags else "",
            "secondary_diagnosis_1_name": secondary_diags[0].diagnosis_name if secondary_diags else "",
            "num_transfer": str(transfer_count.get(ep.episode_id, 0)),
            "ward_code_admission": ward_code,
            "los_days": str(los),
            "procedure_1_code": ep_procs[0].procedure_code if ep_procs else "",
            "procedure_1_name": ep_procs[0].procedure_name if ep_procs else "",
            "procedure_1_date": _format_date(ep_procs[0].procedure_date) if ep_procs else "",
            "facility_type": _FACILITY_TYPE_CODE.get(ctx.facility.facility_type, "99"),
            "prefecture_code": ctx.facility.prefecture_code,
            "total_bed_count": str(ctx.facility.bed_count),
            "insurer_number": payer.insurer_number or "" if payer else "",
            "age_at_admission": str(_calc_age(patient.birth_date, ep.admission_date)),
        }
        records.append(record)

    output_path = ctx.config.output_dir / "form1.csv"
    serialize_csv(records, schema, output_path)
    ctx.output_files["form1"] = output_path
