
from montgomery import MontgomeryContext


def main():
    N = 339
    a = 18
    b = 512
    exp = 64

    ctx = MontgomeryContext(N)

    print("Параметры Монтгомери:")
    for name, value in ctx.parameters().items():
        print(f"{name}: {value}")

    print("\nПреобразование чисел:")

    a_mont = ctx.to_montgomery(a)
    b_mont = ctx.to_montgomery(b)

    print(f"a = {a} -> {a_mont}")
    print(f"b = {b} -> {b_mont}")

    print("\nРедукция REDC:")

    result_mont = ctx.multiply(a_mont, b_mont, trace=True)

    print("Трассировка:")
    print(ctx.last_trace)

    result = ctx.from_montgomery(result_mont)

    print(f"\nРезультат: {a} * {b} mod {N} = {result}")
    print(f"Проверка обычным умножением: {(a * b) % N}")

    print("\nСчётчики операций:")
    print(f"REDC: {ctx.stats.redc}")
    print(f"Умножений: {ctx.stats.multiplications}")
    print(f"Квадратов: {ctx.stats.squarings}\n")

    result = ctx.pow_montgomery(a, exp, trace=True)

    print("Результат:", result)
    print("Ожидаемый результат:", pow(a, exp, N))

    print("\nТрассировка:")

    for step in ctx.last_power_trace:
        print(step)

    print("\nСтатистика:")
    print("REDC:", ctx.stats.redc)
    print("Умножений:", ctx.stats.multiplications)
    print("Квадратов:", ctx.stats.squarings)


if __name__ == "__main__":
    main()
