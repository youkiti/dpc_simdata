"""ファイル間の参照整合性検証."""

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IntegrityError:
    """参照整合性エラー."""

    check: str
    message: str


def _read_csv_column(path: Path, col_index: int, encoding: str = "shift_jis") -> set[str]:
    """CSVファイルの特定列の値集合を返す."""
    values: set[str] = set()
    if not path.exists():
        return values
    with path.open(encoding=encoding) as f:
        for row in csv.reader(f):
            if len(row) > col_index:
                values.add(row[col_index])
    return values


def validate_cross_file_integrity(output_dir: Path) -> list[IntegrityError]:
    """出力ディレクトリ内のファイル間整合性を検証する."""
    errors: list[IntegrityError] = []

    form1 = output_dir / "form1.csv"
    form3 = output_dir / "form3.csv"
    form4 = output_dir / "form4.csv"
    ef_inpatient = output_dir / "ef_inpatient.csv"
    d_file = output_dir / "d_file.csv"
    h_file = output_dir / "h_file.csv"
    k_file = output_dir / "k_file.csv"

    # 施設コードの一致
    facility_codes: set[str] = set()
    for path in [form1, form3, form4, ef_inpatient, d_file, h_file, k_file]:
        if path.exists():
            codes = _read_csv_column(path, 0)
            facility_codes.update(codes)
    if len(facility_codes) > 1:
        errors.append(IntegrityError("facility_code", f"施設コードが複数存在: {facility_codes}"))

    # form1の患者IDがef_inpatient, d_fileにも存在
    if form1.exists():
        form1_episodes = _read_csv_column(form1, 3)  # episode_id

        if ef_inpatient.exists():
            ef_episodes = _read_csv_column(ef_inpatient, 3)
            missing = ef_episodes - form1_episodes
            if missing:
                errors.append(
                    IntegrityError(
                        "ef_inpatient_episodes",
                        f"ef_inpatientにform1にないエピソードID: {missing}",
                    )
                )

        if d_file.exists():
            d_episodes = _read_csv_column(d_file, 3)
            missing = d_episodes - form1_episodes
            if missing:
                errors.append(
                    IntegrityError("d_file_episodes", f"d_fileにform1にないエピソードID: {missing}")
                )

        if h_file.exists():
            h_episodes = _read_csv_column(h_file, 3)
            missing = h_episodes - form1_episodes
            if missing:
                errors.append(
                    IntegrityError("h_file_episodes", f"h_fileにform1にないエピソードID: {missing}")
                )

    # form4はform1の対象をスーパーセットとして含む
    if form1.exists() and form4.exists():
        form1_episodes = _read_csv_column(form1, 3)
        form4_episodes = _read_csv_column(form4, 3)
        missing = form1_episodes - form4_episodes
        if missing:
            errors.append(
                IntegrityError("form4_superset", f"form1にあってform4にないエピソードID: {missing}")
            )

    # k_fileの患者はef_inpatient対象に限る
    if k_file.exists() and ef_inpatient.exists():
        k_patients = _read_csv_column(k_file, 2)
        ef_patients = _read_csv_column(ef_inpatient, 2)
        extra = k_patients - ef_patients
        if extra:
            errors.append(
                IntegrityError("k_file_patients", f"k_fileにef_inpatientにない患者ID: {extra}")
            )

    return errors
