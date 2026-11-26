from cache import PrecomputationCache
from exponentiation import Exponentiation
from montgomery import MontgomeryContext


def print_statistics(algorithm, name):
    print(f"\n{name}")
    print("Результат:", algorithm.result)
    print("Квадраты:", algorithm.stats.squarings)
    print("Умножения:", algorithm.stats.multiplications)
    print("REDC:", algorithm.stats.redc)


def print_exponentiation_statistics(algorithm, name):
    print(f"\n{name}")
    print("Результат:", algorithm.result)

    print("Общая статистика:")
    print("Квадраты:", algorithm.stats.squarings)
    print("Умножения:", algorithm.stats.multiplications)
    print("REDC:", algorithm.stats.redc)

    print("Предвычисления:")
    print("Квадраты:",
          algorithm.precomputation_stats["squarings"])
    print("Умножения:",
          algorithm.precomputation_stats["multiplications"])

    print("Основное вычисление:")
    print("Квадраты:",
          algorithm.execution_stats["squarings"])
    print("Умножения:",
          algorithm.execution_stats["multiplications"])


def main():
    base = 18
    exponent = 64
    modulus = 339

    print("Исходные данные:")
    print(f"Основание: {base}")
    print(f"Показатель: {exponent}")
    print(f"Модуль: {modulus}")

    # Эталонный результат
    expected = pow(base, exponent, modulus)

    # Метод Монтгомери
    montgomery = MontgomeryContext(modulus)

    result_mont = montgomery.pow_montgomery(
        base, exponent, trace=True
    )

    print("\nМетод Монтгомери")
    print("Результат:", result_mont)
    print("Квадраты:", montgomery.stats.squarings)
    print("Умножения:", montgomery.stats.multiplications)
    print("REDC:", montgomery.stats.redc)

    # Бинарный алгоритм слева направо
    binary = Exponentiation()

    result_binary = binary.binary_left_to_right(
        base, exponent, modulus, trace=True
    )

    print("\nБинарный алгоритм слева направо")
    print("Результат:", result_binary)
    print("Квадраты:", binary.stats.squarings)
    print("Умножения:", binary.stats.multiplications)
    print("REDC:", binary.stats.redc)

    # q-арный алгоритм
    q_ary = Exponentiation()

    k = 2

    result_q_ary = q_ary.q_ary(
        base, exponent, modulus, k, trace=True
    )

    q_ary.result = result_q_ary

    print_exponentiation_statistics(
        q_ary,
        f"q-арный алгоритм (q = {2 ** k})"
    )

    # Метод скользящего окна
    window_results = {}

    for w in [2, 3, 4]:

        sliding = Exponentiation()

        result_sliding = sliding.sliding_window(
            base, exponent, modulus, w, trace=True
        )

        sliding.result = result_sliding
        window_results[w] = result_sliding

        print_exponentiation_statistics(
            sliding,
            f"Скользящее окно (w = {w})"
        )

    # Сравнение результатов
    print("\nПроверка результатов")

    print("Библиотечный результат:", expected)

    print("Монтгери:", result_mont == expected)
    print("Бинарный:", result_binary == expected)
    print("q-арный:", result_q_ary == expected)

    for w, result in window_results.items():
        print(
            f"Скользящее окно (w={w}):",
            result == expected
        )

    # Демонстрация кэширования
    print("\n\nПроверка кэширования")

    cache = PrecomputationCache()
    cached_algorithm = Exponentiation()

    # Первый запрос
    result1 = cached_algorithm.q_ary(
        7, 13, 19, 2, cache=cache
    )

    print("\nПервый запрос q-арного метода:")
    print("Результат:", result1)
    print("Попадания:", cache.cache_hits)
    print("Промахи:", cache.cache_misses)
    print(
        "Предвычисления:",
        cached_algorithm.precomputation_stats
    )

    # Второй запрос с теми же параметрами,
    # но другим показателем
    result2 = cached_algorithm.q_ary(
        7, 25, 19, 2, cache=cache
    )

    print("\nВторой запрос q-арного метода:")
    print("Результат:", result2)
    print("Попадания:", cache.cache_hits)
    print("Промахи:", cache.cache_misses)
    print(
        "Предвычисления:",
        cached_algorithm.precomputation_stats
    )

    # Третий запрос с другим основанием
    result3 = cached_algorithm.q_ary(
        5, 13, 19, 2, cache=cache
    )

    print("\nТретий запрос с другим основанием:")
    print("Результат:", result3)
    print("Попадания:", cache.cache_hits)
    print("Промахи:", cache.cache_misses)

    print("\nРазмер кэша:", cache.size)


if __name__ == "__main__":
    main()
