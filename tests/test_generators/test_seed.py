"""SeedManager のテスト."""

from dpc_simdata.generators.seed import SeedManager


class TestSeedManager:
    def test_same_seed_same_result(self) -> None:
        sm1 = SeedManager(42)
        sm2 = SeedManager(42)
        assert sm1.derive_seed("facility") == sm2.derive_seed("facility")

    def test_different_namespace_different_seed(self) -> None:
        sm = SeedManager(42)
        assert sm.derive_seed("facility") != sm.derive_seed("patient")

    def test_different_root_different_seed(self) -> None:
        sm1 = SeedManager(42)
        sm2 = SeedManager(99)
        assert sm1.derive_seed("facility") != sm2.derive_seed("facility")

    def test_rng_reproducible(self) -> None:
        sm = SeedManager(42)
        rng1 = sm.rng("test")
        rng2 = sm.rng("test")
        seq1 = [rng1.randint(0, 100) for _ in range(10)]
        seq2 = [rng2.randint(0, 100) for _ in range(10)]
        assert seq1 == seq2

    def test_rng_independent(self) -> None:
        sm = SeedManager(42)
        rng_a = sm.rng("a")
        rng_b = sm.rng("b")
        seq_a = [rng_a.randint(0, 100) for _ in range(10)]
        seq_b = [rng_b.randint(0, 100) for _ in range(10)]
        assert seq_a != seq_b

    def test_root_seed_property(self) -> None:
        sm = SeedManager(123)
        assert sm.root_seed == 123
