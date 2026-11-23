
from montgomery import MontgomeryContext
from exponentiation import Exponentiation


def main():
    base = 7
    exponent = 13
    modulus = 19

    print("Исходные данные:")
    print(f"Основание: {base}")
    print(f"Показатель: {exponent}")
    print(f"Модуль: {modulus}")

    # 1. Возведение в степень методом Монтгомери
    montgomery = MontgomeryContext(modulus)

    result_mont = montgomery.pow_montgomery(
        base, exponent, trace=True
    )

    print("\n=== Метод Монтгомери ===")
    print("Результат:", result_mont)
    print("REDC:", montgomery.stats.redc)
    print("Умножения:", montgomery.stats.multiplications)
    print("Квадраты:", montgomery.stats.squarings)

    # 2. Бинарный алгоритм слева направо
    binary = Exponentiation()

    result_binary = binary.binary_left_to_right(
        base, exponent, modulus, trace=True
    )

    print("\n=== Бинарный алгоритм слева направо ===")
    print("Результат:", result_binary)
    print("REDC:", binary.stats.redc)
    print("Умножения:", binary.stats.multiplications)
    print("Квадраты:", binary.stats.squarings)

    # 3. Проверка результатов
    expected = pow(base, exponent, modulus)

    print("\n=== Проверка ===")
    print("Библиотечный результат:", expected)
    print("Монтгомери:", result_mont == expected)
    print("Бинарный:", result_binary == expected)


if __name__ == "__main__":
    main()
