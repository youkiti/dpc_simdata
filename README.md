# dpc_simdata

DPC提出データ（様式1/3/4、EF統合ファイル、Dファイル、Hファイル、Kファイル）のシミュレーションデータを再現可能に生成するツールです。

## 前提

- 提出仕様のベースライン: 2025-05-30版 実施説明資料
- 参照元一覧: `docs/source_manifest.md`
- 設計・計画: `docs/dpc_plan.md`

## セットアップ

```bash
uv sync --extra dev
```

## 使い方

```bash
# 基本（患者10名、3病棟、seed=42）
uv run python -m dpc_simdata.cli --output-dir output

# 大規模データ（2000名、10病棟、15ヶ月間、整合性検証付き）
uv run python -m dpc_simdata.cli \
  --seed 42 \
  --num-patients 2000 \
  --num-wards 10 \
  --admission-start 202501 \
  --admission-end 202603 \
  --year-month 202603 \
  --output-dir output \
  --validate
```

### CLIオプション

| オプション | デフォルト | 説明 |
|---|---|---|
| `--seed` | 42 | ルートシード（同じ値で同じデータを再現） |
| `--year-month` | 202504 | データ対象年月（YYYYMM） |
| `--num-patients` | 10 | 生成する患者数 |
| `--num-wards` | 3 | 生成する病棟数 |
| `--admission-start` | - | 入院期間の開始年月（YYYYMM） |
| `--admission-end` | - | 入院期間の終了年月（YYYYMM） |
| `--facility-type` | dpc_target | 施設種別（dpc_target / dpc_prep / fee_for_service） |
| `--output-dir` | output | 出力先ディレクトリ |
| `--validate` | - | 生成後に参照整合性を検証する |

## 生成されるファイル

| ファイル | 単位 | 内容 |
|---|---|---|
| `form3.csv` | 病棟 | 施設情報（病床数、入院基本料等） |
| `form1.csv` | 退院 | 患者属性、病態、診断、手術、転帰 |
| `form4.csv` | 退院 | 医科保険以外の診療情報の有無 |
| `ef_inpatient.csv` | 明細行 | 入院の出来高算定情報 |
| `d_file.csv` | レセプト | DPC包括評価点数・係数（DPC対象病院のみ） |
| `h_file.csv` | 患者日 | 重症度、医療・看護必要度の日次評価 |
| `ef_outpatient.csv` | 明細行 | 外来の出来高算定情報（DPC対象/準備病院のみ） |
| `k_file.csv` | 患者 | 一次共通ID |

出力はすべてShift_JIS、CSV形式です。

## サンプルデータ

| ディレクトリ | 規模 |
|---|---|
| `samples/minimal/` | 患者3名、3病棟 |
| `samples/realistic/` | 患者30名、5病棟 |
| `samples/large/` | 患者2,000名、10病棟、2025-01〜2026-03 |

## 設計

共通の内部エンティティ（施設、病棟、患者、入院エピソード、転棟、診断、処置、請求明細、日次状態、支払情報）から8種の提出データを生成します。個別ファイルを独立に作るのではなく、内部モデルを経由することでファイル間の整合性を保証します。

```
施設・病棟 → 患者 → 入院エピソード → 臨床データ
  → form3 → form1 → form4 → ef_inpatient → d_file → h_file → ef_outpatient → k_file
```

詳細は `docs/dpc_plan.md` を参照してください。

## テスト

```bash
uv run pytest           # 全テスト実行
uv run ruff check src/  # リンター
```

## 技術スタック

- Python 3.12+
- Pydantic v2（内部モデル）
- PyYAML（スキーマ定義）
- pytest / ruff
- uv（パッケージ管理）
