"""再現可能なシード管理."""

import hashlib
import random


class SeedManager:
    """名前空間ベースの決定論的シード管理.

    ルートシードからSHA256ハッシュで名前空間別のサブシードを導出し、
    独立した random.Random インスタンスを返す。
    """

    def __init__(self, root_seed: int = 42) -> None:
        self._root_seed = root_seed

    @property
    def root_seed(self) -> int:
        return self._root_seed

    def derive_seed(self, namespace: str) -> int:
        """名前空間文字列から決定論的にサブシードを導出する."""
        data = f"{self._root_seed}:{namespace}".encode()
        digest = hashlib.sha256(data).digest()
        return int.from_bytes(digest[:8], "big")

    def rng(self, namespace: str) -> random.Random:
        """名前空間に対応する独立した Random インスタンスを返す."""
        return random.Random(self.derive_seed(namespace))
