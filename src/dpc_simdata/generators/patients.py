"""患者マスタの生成."""

from datetime import date

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.patient import Patient, Sex

# カナ姓・名のプール（シミュレーション用）
_KANA_SEI = ["ヤマダ", "サトウ", "スズキ", "タナカ", "ワタナベ", "イトウ", "ナカムラ", "コバヤシ", "ヨシダ", "ヤマモト"]
_KANA_MEI_M = ["タロウ", "ジロウ", "ケンイチ", "ヒロシ", "ダイスケ", "ユウタ", "ショウタ", "コウジ", "マサキ", "アキラ"]
_KANA_MEI_F = ["ハナコ", "ヨウコ", "ケイコ", "ミキ", "アイ", "ユカ", "サクラ", "カオリ", "マイ", "リナ"]


def generate_patients(ctx: GenerationContext) -> None:
    """患者を生成し、コンテキストに設定する."""
    rng = ctx.seed_manager.rng("patient")
    patients: list[Patient] = []

    # 基準日: 調査対象月の1日
    ym = ctx.config.target_year_month
    ref_year = int(ym[:4])

    for i in range(ctx.config.num_patients):
        sex = rng.choice([Sex.MALE, Sex.FEMALE])

        # 年齢: 0〜99歳
        age = rng.randint(0, 99)
        birth_year = ref_year - age
        birth_month = rng.randint(1, 12)
        max_day = 28  # 全月で安全な日数
        birth_day = rng.randint(1, max_day)
        birth_date = date(birth_year, birth_month, birth_day)

        sei = rng.choice(_KANA_SEI)
        mei = rng.choice(_KANA_MEI_M if sex == Sex.MALE else _KANA_MEI_F)

        postal = f"{rng.randint(1000000, 9999999)}"

        patients.append(
            Patient(
                patient_id=f"P{i + 1:04d}",
                birth_date=birth_date,
                sex=sex,
                kana_name=f"{sei} {mei}",
                postal_code=postal,
            )
        )

    ctx.patients = patients
