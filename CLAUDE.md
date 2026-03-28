# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DPC提出データ（様式1/3/4、EF統合ファイル、D/H/Kファイル）のシミュレーションデータを再現可能に生成するためのリポジトリ。仕様のベースラインは2025-05-30版の実施説明資料。ドキュメントは日本語で記述する。

計画書・フェーズ定義・ディレクトリ構成・リスク一覧は `docs/dpc_plan.md` を参照。進捗状況は git log やディレクトリ構造から判断すること。

## Technology Decisions

- **言語:** Python 3.12+
- **パッケージ管理:** uv（pip互換、lockファイルあり）
- **スキーマ定義:** YAML（`schemas/` 配下）
- **テストフレームワーク:** pytest
- **リンター/フォーマッター:** ruff
- **未決定事項:** CLI フレームワーク（click / typer / argparse）は Phase 4 開始時に決定する

上記以外の言語やツールチェーンを導入する場合は、この文書を先に更新すること。

## Architecture: Internal Model → Output Files

シミュレーションは共通の内部エンティティから8種の提出データを生成する設計。個別ファイルを独立に作るのではなく、内部モデルを経由することでファイル間の整合性を保証する。

**内部エンティティ（10種）:** facility, ward, patient, admission_episode, transfer_event, daily_status, claim_line, diagnosis, procedure, payer_context

**出力データセット（8種）:** form1, form3, form4, ef_inpatient, ef_outpatient, d_file, h_file, k_file

**生成順序の依存関係:** 施設・病棟マスタ → 患者マスタ → 入院エピソード・転棟 → form3 → form1 → form4 → ef_inpatient → d_file → h_file → ef_outpatient → k_file

## Key Consistency Constraints

ファイル間で以下の整合性を維持する必要がある：
- 施設コード・病棟コード・診療科・提出対象月がファイル間で矛盾しない
- 患者匿名IDが調査期間を通じて一貫する
- form1の入退院期間とh_fileの日次レコード範囲が一致する
- form1の入院エピソードとef_inpatient・d_fileの請求期間が一致する
- form4の対象症例範囲とform1の対象症例範囲の違いを正しく表現する（form4は医科保険以外の入院も対象に含む）
- k_fileの対象はef_inpatientに含まれる症例に限る
- 外来データを作る場合、施設種別とef_outpatientの作成要否が一致する

整合性制約の全体像は `docs/dpc_plan.md` Section 5 を参照。

## Design Principles

- 固定seedで毎回同じデータを生成できること（再現性）
- まず構造的妥当性と相互参照の整合性を優先し、現実的な分布は次段階
- 合成データのみ使用（実データは使わない）
