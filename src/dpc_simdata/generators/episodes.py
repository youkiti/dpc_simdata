"""入院エピソード・転棟イベントの生成."""

from datetime import date, timedelta

from dpc_simdata.generators.registry import GenerationContext
from dpc_simdata.models.admission import (
    AdmissionEpisode,
    AdmissionRoute,
    DischargeStatus,
    PayerType,
    TransferEvent,
    TransferReason,
)

# シミュレーション用DPCコードプール（14桁）
_DPC_CODES = [
    "010010xx99x0xx",  # 脳腫瘍
    "010060x2990401",  # 脳梗塞
    "040080x099x0xx",  # 肺炎
    "040081xx99x0xx",  # 誤嚥性肺炎
    "050050xx9910xx",  # 狭心症
    "060010xx99x40x",  # 食道悪性腫瘍
    "060340xx03x00x",  # 胆管結石
    "100380xxxxxxxx",  # 体液量減少症
    "110310xx99xxxx",  # 腎臓または尿路の感染症
    "160800xx01xxxx",  # 股関節大腿近位骨折
]

# ICDコード対応（DPCコードと簡易対応）
_ICD_CODES = ["C71", "I63", "J18", "J69", "I20", "C15", "K80", "E86", "N39", "S72"]


def _parse_ym_to_date(ym: str) -> date:
    """YYYYMM文字列を月初のdateに変換する."""
    return date(int(ym[:4]), int(ym[4:6]), 1)


def generate_episodes(ctx: GenerationContext) -> None:
    """入院エピソードと転棟イベントを生成し、コンテキストに設定する."""
    assert ctx.facility is not None
    assert len(ctx.patients) > 0
    assert len(ctx.wards) > 0

    rng = ctx.seed_manager.rng("episode")
    episodes: list[AdmissionEpisode] = []
    transfers: list[TransferEvent] = []

    cfg = ctx.config

    # 入院期間の決定
    if cfg.admission_start and cfg.admission_end:
        range_start = _parse_ym_to_date(cfg.admission_start)
        range_end = _parse_ym_to_date(cfg.admission_end)
        # range_endの月末まで含む
        if range_end.month == 12:
            range_end_last = date(range_end.year + 1, 1, 1) - timedelta(days=1)
        else:
            range_end_last = date(range_end.year, range_end.month + 1, 1) - timedelta(days=1)
        total_days = (range_end_last - range_start).days
    else:
        ym = cfg.target_year_month
        range_start = _parse_ym_to_date(ym) - timedelta(days=15)
        total_days = 35
        range_end_last = range_start + timedelta(days=total_days)

    for i, patient in enumerate(ctx.patients):
        # 入院日: 期間内のランダムな日
        offset = rng.randint(0, max(0, total_days - 1))
        admission_date = range_start + timedelta(days=offset)

        # 在院日数: 3〜30日
        los = rng.randint(3, 30)
        discharge_date = admission_date + timedelta(days=los)

        dpc_idx = rng.randint(0, len(_DPC_CODES) - 1)
        route = rng.choice(list(AdmissionRoute))
        discharge_status = rng.choice([DischargeStatus.HOME, DischargeStatus.HOME, DischargeStatus.TRANSFER_OUT])

        # 支払区分: 大半は社保/国保/後期高齢
        payer = rng.choice([
            PayerType.SOCIAL_INSURANCE,
            PayerType.SOCIAL_INSURANCE,
            PayerType.NATIONAL_INSURANCE,
            PayerType.LATE_ELDERLY,
            PayerType.LATE_ELDERLY,
        ])

        episode_id = f"E{i + 1:04d}"
        episodes.append(
            AdmissionEpisode(
                episode_id=episode_id,
                facility_code=ctx.facility.facility_code,
                patient_id=patient.patient_id,
                admission_date=admission_date,
                discharge_date=discharge_date,
                discharge_status=discharge_status,
                dpc_code=_DPC_CODES[dpc_idx],
                main_diagnosis_icd=_ICD_CODES[dpc_idx],
                admission_route=route,
                payer_type=payer,
            )
        )

        # 転棟: 在院7日以上の場合に一定確率で発生
        if los >= 7 and rng.random() < 0.3 and len(ctx.wards) >= 2:
            transfer_day = rng.randint(2, los - 2)
            from_ward = ctx.wards[0]
            to_ward = rng.choice(ctx.wards[1:])
            transfers.append(
                TransferEvent(
                    episode_id=episode_id,
                    transfer_date=admission_date + timedelta(days=transfer_day),
                    from_ward_code=from_ward.ward_code,
                    to_ward_code=to_ward.ward_code,
                    reason=rng.choice(list(TransferReason)),
                )
            )

    ctx.episodes = episodes
    ctx.transfers = transfers
