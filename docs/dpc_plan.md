# DPC specification review and simulation plan

## 1. Purpose

このリポジトリの目的は、DPC提出データの公開仕様を最新版で固定し、その仕様に沿ったシミュレーションデータを継続的に生成できる状態を作ることです。

本計画では、まず提出仕様の基準資料を明確化し、そのうえで各データの依存関係、生成順序、実装上の未解決事項を整理します。

## 2. Scope and assumptions

- 対象は「DPCの評価・検証等に係る調査（退院患者調査）」の提出データ一式とする
- ここでいう「各データ」は、様式1、様式3、様式4、入院EF統合ファイル、外来EF統合ファイル、Dファイル、Hファイル、Kファイルを指す
- 2026-03-28時点で、厚生労働省の公式掲載で確認できた提出仕様の最新版は 2025-05-30 版
- 2026年度版の実施説明資料は、確認できた公式掲載範囲では未公開のため、当面は 2025年度版をベースラインとする
- シミュレーションは実データを使わず、完全に合成した患者・入院・請求イベントから生成する
- まずは「構造的に妥当で、相互参照が崩れない」ことを優先し、医療現場の発生分布に近づけるのは次段階とする

## 3. Latest official sources checked

2026-03-28時点で確認した一次情報は以下です。

| Source | Checked result | Use |
| --- | --- | --- |
| `令和6年度診療報酬改定について` | 関連情報として `2025年度（令和7年度）DPCの評価・検証等に係る調査（退院患者調査）実施説明資料` と変更履歴が掲載されている | 提出仕様の公式入口 |
| `2025年度（令和7年度）DPCの評価・検証等に係る調査（退院患者調査）実施説明資料` | 文書先頭に `2025年5月30日時点` とある | 様式1、様式3、様式4、D、EF、H、K の基準仕様 |
| `変更履歴（DPC）20250401版からの変更箇所` | 2025-04-01版から 2025-05-30版への差分が1ページで整理されている | 差分確認の起点 |
| `診断群分類（DPC）電子点数表について` | 公式ページ上で最新の正式版更新日が `令和8年3月17日` | DPCコード、点数、分類の最新参照 |
| `DPC/PDPS傷病名コーディングテキスト 改定版（第6版）` | `令和6年6月` 版 | 様式1やDPCコーディングの補助資料 |

参照URL:

- <https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00045.html>
- <https://www.mhlw.go.jp/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/dl/dpc_setumeishiryou_r08.pdf>
- <https://www.mhlw.go.jp/content/12404000/setumei_rireki20250530.pdf>
- <https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000198757_00008.html>
- <https://www.mhlw.go.jp/content/12404000/001394024.pdf>

## 4. Dataset inventory

| Dataset | Unit | Summary | Main dependencies | Notes for simulation |
| --- | --- | --- | --- | --- |
| `form1` | 患者・退院または転棟単位 | 患者属性、病態、診断、手術、転帰など | 患者マスタ、入院エピソード、診断・処置イベント | 退院単位だが転棟時の分割や7日以内再入院の扱いに注意 |
| `form3` | 医療機関単位 | 病床数、入院基本料、病棟コード、算定状況など | 施設マスタ、病棟マスタ | 患者単位ではなく施設単位 |
| `form4` | 退院単位 | 医科保険以外の診療情報の有無 | 入院エピソード、支払区分 | 自費、健診、労災のみ入院も対象に含む |
| `ef_inpatient` | 月次・レセプト明細行単位 | 入院患者の出来高算定情報 | 入院エピソード、診療行為イベント、コード表 | E/F統合後の提出を前提にする |
| `ef_outpatient` | 月次・レセプト明細行単位 | 外来患者の出来高算定情報と病名情報 | 外来受診、診療行為イベント、コード表 | 対象施設が限定される |
| `d_file` | 月次・レセプト単位 | 包括評価点数、係数、出来高理由コードなど | DPC分類、包括算定ロジック、入院請求 | DPC対象病院のみ |
| `h_file` | 月次・患者日単位 | 重症度、医療・看護必要度の評価項目 | 日次入院状態、病棟、看護必要度評価 | 1日ごとのレコード生成が必要 |
| `k_file` | 月次・患者単位 | 生年月日、カナ氏名、性別から作られる一次共通ID | 患者マスタ、入院EF対象症例 | 生成自体は支援ツール依存のため注意 |

## 5. What must be consistent across files

シミュレーションでは、単に個別ファイルが作れるだけでは不十分です。少なくとも以下の整合性を維持する必要があります。

- 施設コード、病棟コード、診療科、提出対象月がファイル間で矛盾しない
- 1患者の匿名IDが調査期間を通じて一貫する
- `form1` の入退院期間と `h_file` の日次レコード範囲が一致する
- `form1` の入院エピソードと `ef_inpatient`、`d_file` の請求期間が一致する
- `form4` の対象症例範囲と `form1` の対象症例範囲の違いを正しく表現する
- `k_file` の対象は `ef_inpatient` に含まれる症例に限る
- 外来データを作る場合、施設種別と `ef_outpatient` の作成要否が一致する

## 6. Recommended implementation order

### Phase 1. Lock the baseline

- 仕様の基準資料、確認日、URLをこの文書で固定する
- 2026年度版の公開有無を監視対象にする

完了条件:

- ベースライン資料と日付が明記されている
- 差分確認に使う資料が決まっている

### Phase 2. Define a canonical internal model

先に出力ファイルを作り始めるのではなく、共通の内部モデルを決めます。

必要な内部エンティティ:

- `facility`
- `ward`
- `patient`
- `admission_episode`
- `transfer_event`
- `daily_status`
- `claim_line`
- `diagnosis`
- `procedure`
- `payer_context`

完了条件:

- 各提出データがどの内部エンティティから生成されるか対応表がある

### Phase 3. Make field-level schemas machine-readable

実施説明資料から、各データの項目、型、必須性、コード体系、繰り返し条件を切り出し、機械可読な定義にします。

想定成果物:

- `schemas/form1.yaml`
- `schemas/form3.yaml`
- `schemas/form4.yaml`
- `schemas/ef_inpatient.yaml`
- `schemas/ef_outpatient.yaml`
- `schemas/d_file.yaml`
- `schemas/h_file.yaml`
- `schemas/k_file.yaml`

完了条件:

- すべての対象データに対して、列定義と生成元の対応が残っている

### Phase 4. Build generators in dependency order

推奨順:

1. 施設・病棟マスタ
2. 患者マスタ
3. 入院エピソードと転棟イベント
4. `form3`
5. `form1`
6. `form4`
7. `ef_inpatient`
8. `d_file`
9. `h_file`
10. `ef_outpatient`
11. `k_file`

この順にする理由:

- `form3` は施設情報だけで作れる
- `form1` と `form4` は入院エピソードが確定すれば生成しやすい
- `ef_inpatient`、`d_file`、`h_file` は診療行為や日次状態を持ってからの方が整合性を保ちやすい
- `k_file` は最終的な患者属性と対象症例集合が確定してから作る方が安全

完了条件:

- 固定seedで毎回同じデータが生成できる
- 最小サンプルとやや現実的なサンプルの両方を出せる

### Phase 5. Add validators and tests

最低限必要な検証:

- 列数、型、桁数、コード値の検証
- 月次ファイルの対象月検証
- 患者・入院・請求の参照整合性検証
- データ間の件数突合
- DPC対象病院のみ必要なファイルが出ているかの検証

完了条件:

- 出力直後に自動検証が走る
- 仕様差分を取り込んだときに壊れた箇所が分かる

## 7. Suggested repository layout

```text
docs/
  dpc_plan.md
  source_manifest.md
  spec_notes/
schemas/
samples/
  minimal/
  realistic/
src/
  dpc_simdata/
tests/
```

## 8. Risks and open questions

- `k_file` の一次共通IDの厳密な生成仕様は、公開資料上では「支援ツールで自動作成」とされており、同一値再現の方法を別途確認する必要がある
- `ef_inpatient` と `ef_outpatient` は提出時にE/F統合が必要で、統合後の正確なレイアウトや支援ツール依存挙動の確認が必要
- `h_file` の実運用に近いデータを作るには、実施説明資料だけでなく評価票の手引きも参照した方が良い
- DPCコードの妥当な分布を作るには、実施説明資料だけでなく最新の電子点数表を取り込む必要がある
- 2026年度版の実施説明資料が公開された時点で、ベースライン差し替えの見直しが必要
- もし最終目的が「提出データ」ではなく「研究提供用の匿名化DPCデータ」であれば、対象仕様そのものが変わるためスコープ確認が必要

## 9. Immediate next actions

`docs/source_manifest.md` は作成済みです。直近では以下の順で進めるのが妥当です。

1. 各データの項目一覧を手で抜き出し、YAMLまたはCSVで管理する
2. 共通内部モデルを定義する
3. `form3` と `form1` から最小シミュレーターを作る
4. EF、D、H、Kを順次つなぐ
5. 自動検証を追加して差分取り込みに備える

この文書は、2026-03-28時点の公開一次情報に基づく初版です。


