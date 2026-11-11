import pytest

from connect_four.evaluation.metrics import bootstrap_ci, wilson_interval


def test_wilson_interval_matches_hand_calculation_for_200_wins() -> None:
    lower, upper = wilson_interval(200, 200)

    assert lower == pytest.approx(200 / (200 + 1.96**2))
    assert upper == pytest.approx(1.0)


def test_wilson_interval_contains_observed_proportion() -> None:
    lower, upper = wilson_interval(100, 200)

    assert lower < 0.5 < upper


@pytest.mark.parametrize(
    ("wins", "total", "z"),
    [(0, 0, 1.96), (-1, 10, 1.96), (11, 10, 1.96), (2, 10, float("nan"))],
)
def test_wilson_interval_rejects_invalid_input(
    wins: float, total: int, z: float
) -> None:
    with pytest.raises(ValueError):
        wilson_interval(wins, total, z)


def test_bootstrap_ci_is_reproducible_with_seed() -> None:
    samples = [0.0, 0.25, 0.75, 1.0]

    first = bootstrap_ci(samples, n_resamples=1_000, seed=42)
    second = bootstrap_ci(samples, n_resamples=1_000, seed=42)

    assert first == second
    assert first[0] <= sum(samples) / len(samples) <= first[1]


def test_bootstrap_ci_is_exact_for_constant_samples() -> None:
    assert bootstrap_ci([3.5] * 8, n_resamples=100, seed=5) == (3.5, 3.5)


@pytest.mark.parametrize(
    ("samples", "n_resamples", "alpha"),
    [([], 100, 0.05), ([1.0], 0, 0.05), ([1.0], 100, 0), ([float("inf")], 100, 0.05)],
)
def test_bootstrap_ci_rejects_invalid_input(
    samples: list[float], n_resamples: int, alpha: float
) -> None:
    with pytest.raises(ValueError):
        bootstrap_ci(samples, n_resamples=n_resamples, alpha=alpha, seed=0)
