from dataclasses import dataclass


@dataclass
class ExponentiationStats:
    squarings: int = 0
    multiplications: int = 0
    redc: int = 0

    def reset(self):
        self.squarings = 0
        self.multiplications = 0
        self.redc = 0


class Exponentiation:
    """
    Класс реализаций алгоритмов модульного возведения в степень
    """

    def __init__(self):
        self.stats = ExponentiationStats()
        self.last_trace = []

    def binary_left_to_right(
        self,
        base: int,
        exponent: int,
        modulus: int,
        trace: bool = False
    ) -> int:
        """
        Бинарный алгоритм возведения в степень слева направо
        """

        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("Основание должно быть целым числом")

        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError("Показатель должен быть целым числом")

        if not isinstance(modulus, int) or isinstance(modulus, bool):
            raise TypeError("Модуль должен быть целым числом")

        if modulus <= 0:
            raise ValueError("Модуль должен быть положительным")

        if exponent < 0:
            raise ValueError("Показатель не может быть отрицательным")

        self.stats.reset()
        self.last_trace = []

        # Особый случай: N = 1
        if modulus == 1:
            return 0

        # Особый случай: x = 0
        if exponent == 0:
            return 1 % modulus

        # 1. Подготовка
        base %= modulus

        binary_exponent = bin(exponent)[2:]

        if trace:
            self.last_trace.append({
                "stage": "preparation",
                "base": base,
                "exponent": exponent,
                "binary_exponent": binary_exponent,
                "modulus": modulus,
            })

        # 2. Инициализация аккумулятора
        accumulator = base

        if trace:
            self.last_trace.append({
                "stage": "initialization",
                "accumulator": accumulator,
            })

        # 3. Обработка битов слева направо
        for position in range(1, len(binary_exponent)):

            bit = int(binary_exponent[position])

            # Возведение в квадрат
            accumulator = (accumulator * accumulator) % modulus
            self.stats.squarings += 1

            if trace:
                self.last_trace.append({
                    "stage": "squaring",
                    "bit_index": len(binary_exponent) - 1 - position,
                    "bit": bit,
                    "accumulator": accumulator,
                })

            # Умножение на основание при бите 1
            if bit == 1:

                accumulator = (accumulator * base) % modulus
                self.stats.multiplications += 1

                if trace:
                    self.last_trace.append({
                        "stage": "multiplication",
                        "bit_index": len(binary_exponent) - 1 - position,
                        "bit": bit,
                        "accumulator": accumulator,
                    })

        if trace:
            self.last_trace.append({
                "stage": "result",
                "result": accumulator,
            })

        return accumulator
