"""診断・処置・請求明細の生成."""

from datetime import timedelta

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.clinical import (
    ClaimCategory,
    ClaimLine,
    Diagnosis,
    DiagnosisCategory,
    Procedure,
)
from dpc_simdata.models.daily import DailyStatus, NursingNecessity
from dpc_simdata.models.payer import PayerContext

# シミュレーション用の副傷病名プール
_SECONDARY_DIAGNOSES = [
    ("E119", "2型糖尿病"),
    ("I10", "本態性高血圧症"),
    ("E785", "高脂血症"),
    ("J189", "肺炎"),
    ("N189", "慢性腎臓病"),
    ("E149", "糖尿病"),
    ("I489", "心房細動"),
    ("K219", "胃食道逆流症"),
]

# シミュレーション用の診療行為プール
_PROCEDURES = [
    ("150289610", "血液学的検査判断料", 125),
    ("160008510", "画像診断管理加算", 70),
    ("120002910", "処方料", 42),
    ("130001610", "手術後医学管理料", 1188),
    ("140000710", "創傷処理", 470),
    ("150150810", "生化学的検査判断料", 144),
    ("160006410", "コンピューター断層撮影診断料", 450),
    ("170010810", "リハビリテーション総合計画評価料", 300),
]


def generate_clinical(ctx: GenerationContext) -> None:
    """診断・処置・請求明細・支払コンテキストを生成する."""
    assert len(ctx.episodes) > 0

    rng = ctx.seed_manager.rng("clinical")
    diagnoses: list[Diagnosis] = []
    procedures: list[Procedure] = []
    claim_lines: list[ClaimLine] = []
    payer_contexts: list[PayerContext] = []
    daily_statuses: list[DailyStatus] = []

    for ep in ctx.episodes:
        # 主傷病の診断
        diagnoses.append(
            Diagnosis(
                episode_id=ep.episode_id,
                icd_code=ep.main_diagnosis_icd,
                diagnosis_category=DiagnosisCategory.MAIN,
                diagnosis_name=f"主傷病_{ep.main_diagnosis_icd}",
                onset_date=ep.admission_date,
            )
        )

        # 入院契機病名
        diagnoses.append(
            Diagnosis(
                episode_id=ep.episode_id,
                icd_code=ep.main_diagnosis_icd,
                diagnosis_category=DiagnosisCategory.TRIGGER,
                diagnosis_name=f"入院契機_{ep.main_diagnosis_icd}",
                onset_date=ep.admission_date,
            )
        )

        # 副傷病: 0〜3個
        num_secondary = rng.randint(0, 3)
        selected = rng.sample(_SECONDARY_DIAGNOSES, min(num_secondary, len(_SECONDARY_DIAGNOSES)))
        for icd, name in selected:
            diagnoses.append(
                Diagnosis(
                    episode_id=ep.episode_id,
                    icd_code=icd,
                    diagnosis_category=DiagnosisCategory.SECONDARY,
                    diagnosis_name=name,
                )
            )

        # 処置: 1〜3件
        num_procs = rng.randint(1, 3)
        selected_procs = rng.sample(_PROCEDURES, min(num_procs, len(_PROCEDURES)))
        for code, name, _tensu in selected_procs:
            proc_offset = rng.randint(0, max(0, (ep.discharge_date - ep.admission_date).days - 1))
            procedures.append(
                Procedure(
                    episode_id=ep.episode_id,
                    procedure_code=code,
                    procedure_name=name,
                    procedure_date=ep.admission_date + timedelta(days=proc_offset),
                )
            )

        # 請求明細: 各処置に対応する明細行
        claim_month = f"{ep.admission_date.year}{ep.admission_date.month:02d}"
        for code, name, tensu in selected_procs:
            qty = rng.randint(1, 5)
            claim_lines.append(
                ClaimLine(
                    episode_id=ep.episode_id,
                    claim_month=claim_month,
                    shinryo_code=code,
                    shinryo_name=name,
                    tensu=tensu,
                    quantity=qty,
                    category=rng.choice([ClaimCategory.FEE_FOR_SERVICE, ClaimCategory.INCLUSIVE]),
                )
            )

        # 日次状態: 入院日から退院日まで1日1レコード
        if ep.discharge_date:
            ward_code = ctx.wards[0].ward_code if ctx.wards else "01"
            los = (ep.discharge_date - ep.admission_date).days
            for day_offset in range(los):
                daily_statuses.append(
                    DailyStatus(
                        episode_id=ep.episode_id,
                        status_date=ep.admission_date + timedelta(days=day_offset),
                        ward_code=ward_code,
                        nursing_necessity=NursingNecessity(
                            a_score=rng.randint(0, 5),
                            b_score=rng.randint(0, 5),
                            c_score=rng.randint(0, 2),
                        ),
                    )
                )

        # 支払コンテキスト
        payer_contexts.append(
            PayerContext(
                episode_id=ep.episode_id,
                payer_type=ep.payer_type,
                insurer_number=f"{rng.randint(10000000, 99999999)}" if ep.payer_type.value != "self_pay" else None,
            )
        )

    ctx.diagnoses = diagnoses
    ctx.procedures = procedures
    ctx.claim_lines = claim_lines
    ctx.payer_contexts = payer_contexts
    ctx.daily_statuses = daily_statuses
