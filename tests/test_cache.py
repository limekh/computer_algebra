import pytest

from cache import PrecomputationCache
from exponentiation import Exponentiation


def test_q_ary_cache_reuse():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    # Первый запрос: промах.
    result1 = algorithm.q_ary(
        7, 13, 19, 2, cache=cache
    )

    assert result1 == pow(7, 13, 19)
    assert cache.cache_misses == 1
    assert cache.cache_hits == 0

    # Проверяем, что предвычисления выполнены
    assert algorithm.precomputation_stats["multiplications"] == 3

    # Второй запрос
    result2 = algorithm.q_ary(
        7, 25, 19, 2, cache=cache
    )

    assert result2 == pow(7, 25, 19)
    assert cache.cache_hits == 1
    assert cache.cache_misses == 1

    # Предвычисления повторно не выполнялись
    assert algorithm.precomputation_stats["multiplications"] == 0


def test_sliding_window_cache_reuse():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    result1 = algorithm.sliding_window(
        7, 13, 19, 3, cache=cache
    )

    assert result1 == pow(7, 13, 19)
    assert cache.cache_misses == 1

    # При w=3 выполняются
    # одно возведение в квадрат и три умножения
    assert algorithm.precomputation_stats["squarings"] == 1
    assert algorithm.precomputation_stats["multiplications"] == 3

    result2 = algorithm.sliding_window(
        7, 25, 19, 3, cache=cache
    )

    assert result2 == pow(7, 25, 19)
    assert cache.cache_hits == 1

    assert algorithm.precomputation_stats["squarings"] == 0
    assert algorithm.precomputation_stats["multiplications"] == 0


def test_cache_different_bases():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    algorithm.q_ary(7, 13, 19, 2, cache=cache)
    algorithm.q_ary(5, 13, 19, 2, cache=cache)

    assert cache.cache_misses == 2
    assert cache.cache_hits == 0
    assert cache.size == 2


def test_cache_different_moduli():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    algorithm.q_ary(7, 13, 19, 2, cache=cache)
    algorithm.q_ary(7, 13, 23, 2, cache=cache)

    assert cache.cache_misses == 2
    assert cache.size == 2


def test_cache_different_parameters():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    algorithm.q_ary(7, 13, 19, 2, cache=cache)
    algorithm.q_ary(7, 13, 19, 3, cache=cache)

    algorithm.sliding_window(7, 13, 19, 2, cache=cache)
    algorithm.sliding_window(7, 13, 19, 3, cache=cache)

    assert cache.cache_misses == 4
    assert cache.cache_hits == 0
    assert cache.size == 4


def test_cache_different_algorithms():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    algorithm.q_ary(7, 13, 19, 2, cache=cache)
    algorithm.sliding_window(7, 13, 19, 2, cache=cache)

    assert cache.cache_misses == 2
    assert cache.size == 2


def test_cache_clear():
    cache = PrecomputationCache()
    algorithm = Exponentiation()

    algorithm.q_ary(7, 13, 19, 2, cache=cache)
    algorithm.q_ary(7, 25, 19, 2, cache=cache)

    assert cache.size == 1
    assert cache.cache_hits == 1

    cache.clear()

    assert cache.size == 0
    assert cache.cache_hits == 0
    assert cache.cache_misses == 0

    algorithm.q_ary(7, 31, 19, 2, cache=cache)

    assert cache.cache_misses == 1