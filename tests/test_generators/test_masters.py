"""施設・病棟マスタ生成のテスト."""

from dpc_simdata.generators.masters import generate_facility
from dpc_simdata.generators.registry import GenerationConfig, GenerationContext
from dpc_simdata.generators.seed import SeedManager


class TestGenerateFacility:
    def _make_context(self, seed: int = 42, num_wards: int = 3) -> GenerationContext:
        config = GenerationConfig(root_seed=seed, num_wards=num_wards)
        return GenerationContext(config=config, seed_manager=SeedManager(seed))

    def test_generates_facility(self) -> None:
        ctx = self._make_context()
        generate_facility(ctx)
        assert ctx.facility is not None
        assert len(ctx.facility.facility_code) == 10

    def test_generates_requested_wards(self) -> None:
        ctx = self._make_context(num_wards=5)
        generate_facility(ctx)
        assert len(ctx.wards) == 5

    def test_ward_beds_sum_to_total(self) -> None:
        ctx = self._make_context()
        generate_facility(ctx)
        ward_beds = sum(w.bed_count for w in ctx.wards)
        assert ward_beds == ctx.facility.bed_count

    def test_reproducible(self) -> None:
        ctx1 = self._make_context(seed=42)
        ctx2 = self._make_context(seed=42)
        generate_facility(ctx1)
        generate_facility(ctx2)
        assert ctx1.facility.facility_code == ctx2.facility.facility_code
        assert [w.bed_count for w in ctx1.wards] == [w.bed_count for w in ctx2.wards]

    def test_different_seed_different_result(self) -> None:
        ctx1 = self._make_context(seed=42)
        ctx2 = self._make_context(seed=99)
        generate_facility(ctx1)
        generate_facility(ctx2)
        assert ctx1.facility.facility_code != ctx2.facility.facility_code

    def test_wards_reference_facility_code(self) -> None:
        ctx = self._make_context()
        generate_facility(ctx)
        for ward in ctx.wards:
            assert ward.facility_code == ctx.facility.facility_code
