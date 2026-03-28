"""samples/ 配下の DPC シミュレーションデータに対する記述統計スクリプト.

Usage:
    uv run --extra analysis python scripts/describe_samples.py [--input-dir samples/large] [--output report.txt]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# スキーマからカラム名を取得
# ---------------------------------------------------------------------------
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

DATASETS = [
    "form3",
    "form1",
    "form4",
    "ef_inpatient",
    "ef_outpatient",
    "d_file",
    "h_file",
    "k_file",
]


def load_column_names(dataset: str) -> list[str]:
    """schemas/<dataset>.yaml から列名リストを返す。"""
    schema_path = SCHEMA_DIR / f"{dataset}.yaml"
    with schema_path.open(encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    return [field["name"] for field in schema["fields"]]


def load_field_types(dataset: str) -> dict[str, str]:
    """schemas/<dataset>.yaml から {列名: type} を返す。"""
    schema_path = SCHEMA_DIR / f"{dataset}.yaml"
    with schema_path.open(encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    return {field["name"]: field.get("type", "string") for field in schema["fields"]}


# ---------------------------------------------------------------------------
# CSV 読み込み
# ---------------------------------------------------------------------------

def read_csv(input_dir: Path, dataset: str) -> pd.DataFrame:
    """ヘッダーなし CSV をスキーマのカラム名で読み込む。"""
    csv_path = input_dir / f"{dataset}.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    columns = load_column_names(dataset)
    df = pd.read_csv(
        csv_path,
        header=None,
        names=columns,
        encoding="cp932",
        dtype=str,  # まず全列文字列で読み込む
    )
    return df


# ---------------------------------------------------------------------------
# 共通記述統計
# ---------------------------------------------------------------------------

def section(title: str) -> str:
    return f"\n{'=' * 60}\n  {title}\n{'=' * 60}\n"


def describe_common(df: pd.DataFrame, dataset: str) -> str:
    """全ファイル共通の記述統計を返す。"""
    lines: list[str] = []
    lines.append(f"行数: {len(df):,}")
    lines.append(f"列数: {len(df.columns)}")

    # 欠損値
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
    lines.append("\n### 欠損値")
    lines.append(f"{'列名':<35} {'欠損数':>8} {'欠損率(%)':>10}")
    lines.append("-" * 55)
    for col in df.columns:
        if missing[col] > 0:
            lines.append(f"{col:<35} {missing[col]:>8,} {missing_pct[col]:>9.1f}%")
    if missing.sum() == 0:
        lines.append("（欠損なし）")

    # 型別集計
    field_types = load_field_types(dataset)

    # 数値列の統計
    numeric_cols = [c for c in df.columns if field_types.get(c) in ("integer", "decimal")]
    if numeric_cols:
        lines.append("\n### 数値列の統計")
        df_num = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        stats = df_num.describe().T
        stats_cols = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
        lines.append(f"{'列名':<35}" + "".join(f"{c:>12}" for c in stats_cols))
        lines.append("-" * (35 + 12 * len(stats_cols)))
        for col in stats.index:
            vals = []
            for c in stats_cols:
                v = stats.loc[col, c]
                if c == "count":
                    vals.append(f"{int(v):>12,}")
                else:
                    vals.append(f"{v:>12.2f}")
            lines.append(f"{col:<35}" + "".join(vals))

    # カテゴリ列
    cat_cols = [c for c in df.columns if field_types.get(c) == "string" and c not in (
        "facility_code", "year_month", "patient_id", "episode_id",
        "postal_code", "insurer_number", "primary_common_id", "kana_name",
    )]
    if cat_cols:
        lines.append("\n### カテゴリ列")
        for col in cat_cols:
            nunique = df[col].nunique()
            top5 = df[col].value_counts().head(5)
            lines.append(f"\n  {col}  (ユニーク数: {nunique})")
            for val, cnt in top5.items():
                pct = cnt / len(df) * 100
                lines.append(f"    {str(val):<40} {cnt:>6,} ({pct:5.1f}%)")

    # 日付列
    date_cols = [c for c in df.columns if field_types.get(c) == "date"]
    if date_cols:
        lines.append("\n### 日付列")
        lines.append(f"{'列名':<35} {'最小':>12} {'最大':>12}")
        lines.append("-" * 60)
        for col in date_cols:
            valid = df[col].dropna()
            if len(valid) > 0:
                lines.append(f"{col:<35} {valid.min():>12} {valid.max():>12}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ファイル固有の集計
# ---------------------------------------------------------------------------

def describe_form1(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### form1 固有集計"]

    # 性別分布
    lines.append("\n  性別分布:")
    sex_map = {"1": "男性", "2": "女性"}
    for val, cnt in df["sex"].value_counts().items():
        lines.append(f"    {sex_map.get(str(val), str(val)):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 年齢分布
    age = pd.to_numeric(df["age_at_admission"], errors="coerce")
    valid_age = age.dropna()
    if len(valid_age) > 0:
        lines.append(f"\n  入院時年齢: mean={valid_age.mean():.1f}, std={valid_age.std():.1f}, "
                      f"min={valid_age.min():.0f}, max={valid_age.max():.0f}")

    # 在院日数
    los = pd.to_numeric(df["los_days"], errors="coerce")
    valid_los = los.dropna()
    if len(valid_los) > 0:
        lines.append(f"  在院日数: mean={valid_los.mean():.1f}, std={valid_los.std():.1f}, "
                      f"median={valid_los.median():.0f}, min={valid_los.min():.0f}, max={valid_los.max():.0f}")

    # 退院先
    lines.append("\n  退院先 (discharge_status):")
    for val, cnt in df["discharge_status"].value_counts().head(5).items():
        lines.append(f"    {str(val):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 入院経路
    lines.append("\n  入院経路 (admission_route):")
    for val, cnt in df["admission_route"].value_counts().head(5).items():
        lines.append(f"    {str(val):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    return "\n".join(lines)


def describe_form3(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### form3 固有集計"]

    bed = pd.to_numeric(df["bed_count"], errors="coerce")
    lines.append(f"  病棟数: {len(df)}")
    lines.append(f"  病床数合計: {bed.sum():.0f}")
    lines.append(f"  病床数平均: {bed.mean():.1f}")

    lines.append("\n  病棟種別 (ward_type):")
    for val, cnt in df["ward_type"].value_counts().items():
        lines.append(f"    {str(val):<20} {cnt:>6,}")

    return "\n".join(lines)


def describe_form4(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### form4 固有集計"]

    for flag_col in ["has_non_medical_insurance", "self_pay_flag", "workers_comp_flag"]:
        ones = (df[flag_col] == "1").sum()
        lines.append(f"  {flag_col}: 1={ones:,} ({ones / len(df) * 100:.1f}%), 0={len(df) - ones:,}")

    return "\n".join(lines)


def describe_ef_inpatient(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### ef_inpatient 固有集計"]

    # レコード種別分布
    lines.append("\n  レコード種別 (record_type):")
    for val, cnt in df["record_type"].value_counts().items():
        lines.append(f"    {str(val):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 点数分布
    tensu = pd.to_numeric(df["tensu"], errors="coerce").dropna()
    if len(tensu) > 0:
        lines.append(f"\n  点数 (tensu): mean={tensu.mean():.1f}, median={tensu.median():.0f}, "
                      f"min={tensu.min():.0f}, max={tensu.max():.0f}")

    total_tensu = pd.to_numeric(df["total_tensu"], errors="coerce").dropna()
    if len(total_tensu) > 0:
        lines.append(f"  合計点数 (total_tensu): mean={total_tensu.mean():.1f}, median={total_tensu.median():.0f}, "
                      f"min={total_tensu.min():.0f}, max={total_tensu.max():.0f}")

    # 患者あたり明細行数
    lines_per_patient = df.groupby("patient_id").size()
    lines.append(f"\n  患者あたり明細行数: mean={lines_per_patient.mean():.1f}, "
                  f"median={lines_per_patient.median():.0f}, "
                  f"min={lines_per_patient.min()}, max={lines_per_patient.max()}")

    return "\n".join(lines)


def describe_ef_outpatient(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### ef_outpatient 固有集計"]

    tensu = pd.to_numeric(df["tensu"], errors="coerce").dropna()
    if len(tensu) > 0:
        lines.append(f"  点数 (tensu): mean={tensu.mean():.1f}, median={tensu.median():.0f}, "
                      f"min={tensu.min():.0f}, max={tensu.max():.0f}")

    # 患者数
    lines.append(f"  ユニーク患者数: {df['patient_id'].nunique()}")

    # 受診日
    visit_dates = df["visit_date"].dropna()
    if len(visit_dates) > 0:
        lines.append(f"  受診日範囲: {visit_dates.min()} ～ {visit_dates.max()}")

    return "\n".join(lines)


def describe_d_file(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### d_file 固有集計"]

    # DPCコード上位
    lines.append("\n  DPCコード上位5:")
    for val, cnt in df["dpc_code"].value_counts().head(5).items():
        lines.append(f"    {str(val):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 包括点数
    inc = pd.to_numeric(df["inclusive_tensu"], errors="coerce").dropna()
    if len(inc) > 0:
        lines.append(f"\n  包括点数 (inclusive_tensu): mean={inc.mean():.1f}, median={inc.median():.0f}, "
                      f"min={inc.min():.0f}, max={inc.max():.0f}")

    total_inc = pd.to_numeric(df["total_inclusive_tensu"], errors="coerce").dropna()
    if len(total_inc) > 0:
        lines.append(f"  合計包括点数: mean={total_inc.mean():.1f}, median={total_inc.median():.0f}, "
                      f"min={total_inc.min():.0f}, max={total_inc.max():.0f}")

    # 係数
    coeff = pd.to_numeric(df["medical_institution_coefficient"], errors="coerce").dropna()
    if len(coeff) > 0:
        lines.append(f"  医療機関係数: mean={coeff.mean():.4f}, min={coeff.min():.4f}, max={coeff.max():.4f}")

    return "\n".join(lines)


def describe_h_file(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### h_file 固有集計"]

    for score_col in ["a_score", "b_score", "c_score"]:
        s = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(s) > 0:
            lines.append(f"  {score_col}: mean={s.mean():.2f}, std={s.std():.2f}, "
                          f"min={s.min():.0f}, max={s.max():.0f}")
            vc = s.value_counts().sort_index()
            for val, cnt in vc.items():
                lines.append(f"    {int(val):>4}: {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 病棟別レコード数
    lines.append("\n  病棟別レコード数:")
    for val, cnt in df["ward_code"].value_counts().items():
        lines.append(f"    {str(val):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 日付カバレッジ
    dates = df["status_date"].dropna()
    if len(dates) > 0:
        lines.append(f"\n  評価日範囲: {dates.min()} ～ {dates.max()}")
        lines.append(f"  ユニーク評価日数: {dates.nunique()}")

    return "\n".join(lines)


def describe_k_file(df: pd.DataFrame) -> str:
    lines: list[str] = ["\n### k_file 固有集計"]

    # 性別
    lines.append("  性別分布:")
    sex_map = {"1": "男性", "2": "女性"}
    for val, cnt in df["sex"].value_counts().items():
        lines.append(f"    {sex_map.get(str(val), str(val)):<20} {cnt:>6,} ({cnt / len(df) * 100:5.1f}%)")

    # 生年月日
    bd = df["birth_date"].dropna()
    if len(bd) > 0:
        lines.append(f"  生年月日範囲: {bd.min()} ～ {bd.max()}")

    return "\n".join(lines)


SPECIFIC_DESCRIBERS = {
    "form1": describe_form1,
    "form3": describe_form3,
    "form4": describe_form4,
    "ef_inpatient": describe_ef_inpatient,
    "ef_outpatient": describe_ef_outpatient,
    "d_file": describe_d_file,
    "h_file": describe_h_file,
    "k_file": describe_k_file,
}


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="DPC シミュレーションデータの記述統計")
    parser.add_argument("--input-dir", type=Path, default=Path("samples/large"),
                        help="入力ディレクトリ (default: samples/large)")
    parser.add_argument("--output", type=Path, default=None,
                        help="出力ファイルパス (省略時は stdout)")
    args = parser.parse_args()

    input_dir: Path = args.input_dir
    if not input_dir.exists():
        print(f"エラー: ディレクトリが見つかりません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    report_lines: list[str] = []
    report_lines.append(f"# DPC シミュレーションデータ 記述統計レポート")
    report_lines.append(f"# 対象: {input_dir.resolve()}")
    report_lines.append("")

    for dataset in DATASETS:
        csv_path = input_dir / f"{dataset}.csv"
        if not csv_path.exists():
            report_lines.append(section(f"{dataset} — ファイルなし"))
            continue

        df = read_csv(input_dir, dataset)
        report_lines.append(section(dataset))
        report_lines.append(describe_common(df, dataset))

        describer = SPECIFIC_DESCRIBERS.get(dataset)
        if describer:
            report_lines.append(describer(df))

    report = "\n".join(report_lines)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"レポートを保存しました: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
