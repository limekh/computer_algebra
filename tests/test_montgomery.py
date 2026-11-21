
import random
import pytest

from montgomery import MontgomeryContext


def test_parameters():
    ctx = MontgomeryContext(19)

    assert ctx.N == 19
    assert ctx.R == 32
    assert ctx.s == 5
    assert ctx.R > ctx.N

    assert (ctx.N * ctx.N_prime + 1) % ctx.R == 0


def test_redc_example():
    ctx = MontgomeryContext(19)

    # 7 и 11 в представлении Монтгомери
    a = ctx.to_montgomery(7)
    b = ctx.to_montgomery(11)

    result = ctx.multiply(a, b)
    result = ctx.from_montgomery(result)

    assert result == (7 * 11) % 19


def test_redc_random():
    rng = random.Random(42)

    moduli = [3, 5, 7, 19, 31, 101, 1009]

    for N in moduli:
        ctx = MontgomeryContext(N)
        r_inverse = ctx._mod_inverse(ctx.R, N)

        for _ in range(500):
            T = rng.randrange(ctx.R * N)

            result = ctx.redc(T)

            expected = (T * r_inverse) % N

            assert result == expected
            assert 0 <= result < N


def test_montgomery_multiplication_random():
    rng = random.Random(42)

    for N in [3, 7, 19, 101, 1009]:
        ctx = MontgomeryContext(N)

        for _ in range(500):
            a = rng.randrange(N)
            b = rng.randrange(N)

            a_mont = ctx.to_montgomery(a)
            b_mont = ctx.to_montgomery(b)

            result = ctx.multiply(a_mont, b_mont)
            result = ctx.from_montgomery(result)

            assert result == (a * b) % N


def test_montgomery_square():
    ctx = MontgomeryContext(19)

    for a in range(19):
        a_mont = ctx.to_montgomery(a)

        result = ctx.square(a_mont)
        result = ctx.from_montgomery(result)

        assert result == (a * a) % 19


def test_conversion():
    ctx = MontgomeryContext(101)

    for value in range(101):
        mont = ctx.to_montgomery(value)
        restored = ctx.from_montgomery(mont)

        assert restored == value


def test_modulus_one():
    ctx = MontgomeryContext(1)

    assert ctx.to_montgomery(100) == 0
    assert ctx.from_montgomery(0) == 0
    assert ctx.multiply(0, 0) == 0
    assert ctx.redc(0) == 0


def test_even_modulus_rejected():
    with pytest.raises(ValueError):
        MontgomeryContext(10)


def test_zero_modulus_rejected():
    with pytest.raises(ValueError):
        MontgomeryContext(0)


def test_negative_modulus_rejected():
    with pytest.raises(ValueError):
        MontgomeryContext(-7)


def test_invalid_redc_input():
    ctx = MontgomeryContext(19)

    with pytest.raises(ValueError):
        ctx.redc(-1)

    with pytest.raises(ValueError):
        ctx.redc(ctx.R * ctx.N)


def test_invalid_residue():
    ctx = MontgomeryContext(19)

    with pytest.raises(ValueError):
        ctx.multiply(19, 1)

    with pytest.raises(ValueError):
        ctx.from_montgomery(-1)


def test_trace():
    ctx = MontgomeryContext(19)

    result = ctx.redc(100, trace=True)

    assert result == ctx.last_trace["result"]
    assert ctx.last_trace["T"] == 100
    assert ctx.last_trace["m"] >= 0
    assert ctx.last_trace["correction_applied"] in (True, False)


def test_operation_counters():
    ctx = MontgomeryContext(19)

    a = ctx.to_montgomery(7)
    b = ctx.to_montgomery(11)

    ctx.reset_stats()

    ctx.multiply(a, b)
    ctx.square(a)

    assert ctx.stats.multiplications == 1
    assert ctx.stats.squarings == 1
    assert ctx.stats.redc == 2



def test_montgomery_power_example():
    ctx = MontgomeryContext(19)

    result = ctx.pow_montgomery(7, 13)

    assert result == 7
    assert result == pow(7, 13, 19)


def test_montgomery_power_random():
    import random

    rng = random.Random(42)

    for N in [3, 7, 19, 31, 101, 1009, 65537]:
        ctx = MontgomeryContext(N)

        for _ in range(100):
            base = rng.randrange(N)
            exponent = rng.randrange(1025)

            result = ctx.pow_montgomery(base, exponent)

            assert result == pow(base, exponent, N)


def test_montgomery_power_zero_exponent():
    ctx = MontgomeryContext(19)

    assert ctx.pow_montgomery(7, 0) == 1
    assert ctx.pow_montgomery(0, 0) == 1


def test_montgomery_power_zero_base():
    ctx = MontgomeryContext(19)

    assert ctx.pow_montgomery(0, 5) == 0


def test_montgomery_power_modulus_one():
    ctx = MontgomeryContext(1)

    assert ctx.pow_montgomery(0, 0) == 0
    assert ctx.pow_montgomery(7, 13) == 0


def test_montgomery_power_negative_exponent():
    ctx = MontgomeryContext(19)

    with pytest.raises(ValueError):
        ctx.pow_montgomery(7, -1)


def test_montgomery_power_trace():
    ctx = MontgomeryContext(19)

    result = ctx.pow_montgomery(7, 13, trace=True)

    assert result == 7

    trace = ctx.last_power_trace

    assert trace[0]["stage"] == "preparation"
    assert trace[1]["stage"] == "initialization"
    assert trace[-1]["stage"] == "conversion"

    # 13 = 1101_2:
    # три возведения в квадрат и два умножения
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


def test_montgomery_power_operation_counters():
    ctx = MontgomeryContext(19)

    ctx.reset_stats()

    result = ctx.pow_montgomery(7, 13)

    assert result == 7

    assert ctx.stats.squarings == 3
    assert ctx.stats.multiplications == 2

    # 1 REDC при переводе основания,
    # 3 REDC при возведении в квадрат,
    # 2 REDC при умножениях,
    # 1 REDC при обратном преобразовании
    assert ctx.stats.redc == 7

