# DPC source manifest

このファイルは、DPCシミュレーション作業で参照する公式ソースを固定するための一覧です。

確認日: 2026-03-28

## Primary sources

| Category | Source | Version or latest date confirmed | Purpose | URL |
| --- | --- | --- | --- | --- |
| Submission spec | 2025年度（令和7年度）DPCの評価・検証等に係る調査（退院患者調査）実施説明資料 | 2025-05-30 | 提出データ全体の基準仕様 | <https://www.mhlw.go.jp/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/dl/dpc_setumeishiryou_r08.pdf> |
| Submission spec diff | 変更履歴（DPC）20250401版からの変更箇所 | 2025-05-30 | 直近差分の確認 | <https://www.mhlw.go.jp/content/12404000/setumei_rireki20250530.pdf> |
| Official index | 令和6年度診療報酬改定について | 2026-03-28時点で 2025年度実施説明資料まで掲載を確認 | 参照先の公式入口 | <https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00045.html> |
| DPC code table | 診断群分類（DPC）電子点数表について | 令和8年3月17日更新 | DPCコード、分類、点数の最新参照 | <https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000198757_00008.html> |
| Coding guidance | DPC/PDPS傷病名コーディングテキスト 改定版（第6版） | 令和6年6月 | ICDコーディングと様式1補助資料 | <https://www.mhlw.go.jp/content/12404000/001394024.pdf> |

## Monitoring targets

| Target | Why it matters | Check timing |
| --- | --- | --- |
| 次年度のDPC実施説明資料 | ベースライン差し替えの可能性がある | 毎月1回、または年度替わり前後 |
| DPC電子点数表の更新 | DPCコードと点数の整合性に影響する | 月1回 |
| DPC変更履歴資料 | 既存スキーマとの差分把握に必要 | 実施説明資料更新時 |

## Notes

- 2026-03-28時点では、提出仕様のベースラインは 2025-05-30 版を採用する
- `k_file` の厳密な生成仕様はこの一覧の資料だけでは十分でない可能性がある
- `h_file` を実運用に近づける場合は、評価票の手引きなど追加資料を別管理する
