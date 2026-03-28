"""CSV形式での出力シリアライザ."""

import csv
from pathlib import Path

from dpc_simdata.schemas.loader import DatasetSchema


def serialize_csv(
    records: list[dict[str, str]],
    schema: DatasetSchema,
    output_path: Path,
) -> Path:
    """レコードリストをスキーマに従いCSVファイルに出力する.

    Args:
        records: フィールド名をキーとする辞書のリスト（値はすべて文字列）
        schema: 出力スキーマ定義
        output_path: 出力先ファイルパス

    Returns:
        出力ファイルパス
    """
    field_names = [f.name for f in sorted(schema.fields, key=lambda f: f.position)]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding=schema.encoding, newline="") as f:
        writer = csv.writer(f, delimiter=schema.delimiter)
        for record in records:
            row = [record.get(name, "") for name in field_names]
            writer.writerow(row)

    return output_path
