"""施設・病棟マスタの生成."""

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.facility import Facility, Ward, WardType

# 病棟種別ごとの入院基本料デフォルト
_NURSING_GRADES: dict[WardType, str] = {
    WardType.GENERAL: "急性期一般入院料1",
    WardType.SPECIFIC: "特定機能病院入院基本料",
    WardType.ICU: "特定集中治療室管理料1",
    WardType.HCU: "ハイケアユニット入院管理料1",
    WardType.NICU: "新生児特定集中治療室管理料1",
    WardType.PSYCHIATRIC: "精神病棟入院基本料",
    WardType.REHABILITATION: "回復期リハ病棟入院料1",
}

# 生成時に使用する病棟種別の優先順（一般病棟を優先）
_WARD_TYPE_POOL: list[WardType] = [
    WardType.GENERAL,
    WardType.GENERAL,
    WardType.ICU,
    WardType.HCU,
    WardType.SPECIFIC,
    WardType.REHABILITATION,
    WardType.PSYCHIATRIC,
    WardType.NICU,
]


def generate_facility(ctx: GenerationContext) -> None:
    """施設と病棟を生成し、コンテキストに設定する."""
    rng = ctx.seed_manager.rng("facility")

    # 都道府県コード（01〜47）
    pref_code = f"{rng.randint(1, 47):02d}"

    # 医療機関コード: 都道府県2桁 + 8桁乱数
    rest = f"{rng.randint(0, 99999999):08d}"
    facility_code = pref_code + rest

    total_beds = rng.randint(100, 600)

    ctx.facility = Facility(
        facility_code=facility_code,
        facility_name=f"シミュレーション病院{facility_code[-4:]}",
        prefecture_code=pref_code,
        facility_type=ctx.config.facility_type,
        bed_count=total_beds,
    )

    # 病棟生成
    num_wards = ctx.config.num_wards
    remaining_beds = total_beds
    wards: list[Ward] = []

    for i in range(num_wards):
        ward_type = _WARD_TYPE_POOL[i % len(_WARD_TYPE_POOL)]

        if i == num_wards - 1:
            ward_beds = remaining_beds
        else:
            avg = remaining_beds // (num_wards - i)
            ward_beds = rng.randint(max(1, avg - 20), avg + 20)
            ward_beds = max(1, min(ward_beds, remaining_beds - (num_wards - i - 1)))
        remaining_beds -= ward_beds

        wards.append(
            Ward(
                facility_code=facility_code,
                ward_code=f"{i + 1:02d}",
                ward_name=f"{ward_type.value}病棟{i + 1}",
                ward_type=ward_type,
                bed_count=ward_beds,
                nursing_grade=_NURSING_GRADES[ward_type],
            )
        )

    ctx.wards = wards
