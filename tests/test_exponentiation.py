import random
import pytest

from exponentiation import Exponentiation


def test_binary_example():
    algorithm = Exponentiation()

    result = algorithm.binary_left_to_right(7, 13, 19)

    assert result == 7
    assert result == pow(7, 13, 19)


def test_binary_random():
    rng = random.Random(42)
    algorithm = Exponentiation()

    for modulus in [1, 2, 3, 7, 19, 31, 100, 101, 1009]:
        for _ in range(100):
            base = rng.randint(-1000, 1000)
            exponent = rng.randint(0, 1024)

            result = algorithm.binary_left_to_right(
                base, exponent, modulus
            )

            assert result == pow(base, exponent, modulus)


def test_zero_exponent():
    algorithm = Exponentiation()

    assert algorithm.binary_left_to_right(7, 0, 19) == 1
    assert algorithm.binary_left_to_right(0, 0, 19) == 1


def test_zero_base():
    algorithm = Exponentiation()

    assert algorithm.binary_left_to_right(0, 5, 19) == 0


def test_modulus_one():
    algorithm = Exponentiation()

    assert algorithm.binary_left_to_right(7, 13, 1) == 0
    assert algorithm.binary_left_to_right(0, 0, 1) == 0


def test_exponent_one():
    algorithm = Exponentiation()

    assert algorithm.binary_left_to_right(7, 1, 19) == 7

    assert algorithm.stats.squarings == 0
    assert algorithm.stats.multiplications == 0


def test_invalid_exponent():
    algorithm = Exponentiation()

    with pytest.raises(ValueError):
        algorithm.binary_left_to_right(7, -1, 19)


def test_invalid_modulus():
    algorithm = Exponentiation()

    with pytest.raises(ValueError):
        algorithm.binary_left_to_right(7, 13, 0)

    with pytest.raises(ValueError):
        algorithm.binary_left_to_right(7, 13, -19)


def test_invalid_types():
    algorithm = Exponentiation()

    with pytest.raises(TypeError):
        algorithm.binary_left_to_right(7.5, 13, 19)

    with pytest.raises(TypeError):
        algorithm.binary_left_to_right(7, 13.5, 19)

    with pytest.raises(TypeError):
        algorithm.binary_left_to_right(7, 13, 19.5)


def test_binary_operation_counters():
    algorithm = Exponentiation()

    result = algorithm.binary_left_to_right(7, 13, 19)

    assert result == 7

    # 13 = 1101
    # Три квадрата и два умножения
    assert algorithm.stats.squarings == 3
    assert algorithm.stats.multiplications == 2
    assert algorithm.stats.redc == 0


def test_binary_trace():
    algorithm = Exponentiation()

    result = algorithm.binary_left_to_right(
        7, 13, 19, trace=True
    )

    assert result == 7

    trace = algorithm.last_trace

    assert trace[0]["stage"] == "preparation"
    assert trace[1]["stage"] == "initialization"
    assert trace[-1]["stage"] == "result"

    squarings = [
        step for step in trace
        if step["stage"] == "squaring"
    ]

    multiplications = [
        step for step in trace
        if step["stage"] == "multiplication"
    ]

    assert len(squarings) == 3
    assert len(multiplications) == 2


def test_q_ary_example():
    algorithm = Exponentiation()

    result = algorithm.q_ary(7, 13, 19, k=2)

    assert result == 7
    assert result == pow(7, 13, 19)


def test_q_ary_random():
    rng = random.Random(42)
    algorithm = Exponentiation()

    for modulus in [1, 2, 3, 7, 19, 31, 101, 1009]:
        for k in [1, 2, 3, 4, 5]:
            for _ in range(30):
                base = rng.randint(-1000, 1000)
                exponent = rng.randint(0, 1024)

                result = algorithm.q_ary(
                    base, exponent, modulus, k
                )

                assert result == pow(base, exponent, modulus)


def test_q_ary_invalid_k():
    algorithm = Exponentiation()

    for k in [0, -1]:
        with pytest.raises(ValueError):
            algorithm.q_ary(7, 13, 19, k)

    for k in [1.5, True, "2"]:
        with pytest.raises(TypeError):
            algorithm.q_ary(7, 13, 19, k)


def test_q_ary_zero_exponent():
    algorithm = Exponentiation()

    assert algorithm.q_ary(7, 0, 19, k=2) == 1


def test_q_ary_modulus_one():
    algorithm = Exponentiation()

    assert algorithm.q_ary(7, 13, 1, k=2) == 0


def test_q_ary_operation_counters():
    algorithm = Exponentiation()

    result = algorithm.q_ary(7, 13, 19, k=2)

    assert result == 7

    # 13 = 31 в системе счисления с основанием 4
    # Предвычисление: 2 умножения
    # Основное вычисление: 2 квадрата и 1 умножение

    assert algorithm.precomputation_stats["multiplications"] == 3

    assert algorithm.execution_stats["squarings"] == 2
    assert algorithm.execution_stats["multiplications"] == 1

    assert algorithm.stats.squarings == 2
    assert algorithm.stats.multiplications == 4
    assert algorithm.stats.redc == 0


def test_q_ary_trace():
    algorithm = Exponentiation()

    result = algorithm.q_ary(
        7, 13, 19, k=2, trace=True
    )

    assert result == 7

    trace = algorithm.last_trace

    assert trace[0]["stage"] == "preparation"

    assert any(
        step["stage"] == "precomputation"
        for step in trace
    )

    assert trace[-1]["stage"] == "result"

