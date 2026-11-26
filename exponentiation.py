from cache import PrecomputationCache
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

        # Подготовка
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

        # Инициализация аккумулятора
        accumulator = base

        if trace:
            self.last_trace.append({
                "stage": "initialization",
                "accumulator": accumulator,
            })

        # Обработка битов слева направо
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

    def q_ary(
        self,
        base: int,
        exponent: int,
        modulus: int,
        k: int,
        trace: bool = False,
        cache: PrecomputationCache | None = None
    ) -> int:
        """
        q-арный алгоритм возведения в степен
        q = 2^k
        """

        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("Основание должно быть целым числом")

        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError("Показатель должен быть целым числом")

        if not isinstance(modulus, int) or isinstance(modulus, bool):
            raise TypeError("Модуль должен быть целым числом")

        if not isinstance(k, int) or isinstance(k, bool):
            raise TypeError("Параметр k должен быть целым числом")

        if modulus <= 0:
            raise ValueError("Модуль должен быть положительным")

        if exponent < 0:
            raise ValueError("Показатель не может быть отрицательным")

        if k < 1:
            raise ValueError("Параметр k должен быть не меньше 1")

        # Сброс статистики и трассировки
        self.stats.reset()
        self.last_trace = []

        self.precomputation_stats = {
            "squarings": 0,
            "multiplications": 0,
            "redc": 0,
        }

        self.execution_stats = {
            "squarings": 0,
            "multiplications": 0,
            "redc": 0,
        }

        if modulus == 1:
            return 0

        if exponent == 0:
            return 1 % modulus

        # Подготовка
        q = 1 << k
        base %= modulus

        # Разложение показателя в системе счисления q
        digits = []
        temp = exponent

        while temp > 0:
            temp, digit = divmod(temp, q)
            digits.append(digit)

        digits.reverse()

        n = len(digits)

        if trace:
            self.last_trace.append({
                "stage": "preparation",
                "base": base,
                "exponent": exponent,
                "k": k,
                "q": q,
                "n": n,
                "digits": digits.copy(),
                "modulus": modulus,
            })

        # Предвычисление степеней основания
        # Или получение из кэша
        cache_key = (
            "q_ary",
            base,
            modulus,
            k,
            "standard"
        )

        table = cache.get(cache_key) if cache is not None else None

        if table is not None:

            if trace:
                self.last_trace.append({
                    "stage": "cache_hit",
                    "algorithm": "q_ary",
                    "cache_key": cache_key,
                })

        else:

            if trace:
                self.last_trace.append({
                    "stage": "cache_miss",
                    "algorithm": "q_ary",
                    "cache_key": cache_key,
                })

            table = [0] * (q + 1)

            table[0] = 1 % modulus
            table[1] = base

            for j in range(2, q + 1):

                table[j] = (
                    table[j - 1] * base
                ) % modulus

                self.stats.multiplications += 1
                self.precomputation_stats["multiplications"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "precomputation",
                        "power": j,
                        "value": table[j],
                    })

            if cache is not None:
                cache.put(cache_key, table)

        # Инициализация аккумулятора
        accumulator = table[digits[0]]

        if trace:
            self.last_trace.append({
                "stage": "initialization",
                "digit": digits[0],
                "accumulator": accumulator,
            })

        # Основное вычисление
        # Обрабатываем оставшиеся цифры слева направо
        for position in range(1, n):

            digit = digits[position]

            # acc = acc^q
            # Поскольку q = 2^k, выполняем k квадратов
            for square_index in range(k):

                accumulator = (
                    accumulator * accumulator
                ) % modulus

                self.stats.squarings += 1
                self.execution_stats["squarings"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "squaring",
                        "digit_index": position,
                        "digit": digit,
                        "square_index": square_index + 1,
                        "accumulator": accumulator,
                    })

            # При нулевой цифре умножение на 1 пропускаем
            if digit != 0:

                accumulator = (
                    accumulator * table[digit]
                ) % modulus

                self.stats.multiplications += 1
                self.execution_stats["multiplications"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "multiplication",
                        "digit_index": position,
                        "digit": digit,
                        "table_value": table[digit],
                        "accumulator": accumulator,
                    })

        if trace:
            self.last_trace.append({
                "stage": "result",
                "result": accumulator,
            })

        return accumulator

    def sliding_window(
        self,
        base: int,
        exponent: int,
        modulus: int,
        w: int,
        trace: bool = False,
        cache: PrecomputationCache | None = None
    ) -> int:
        """
        Возведение в степень методом скользящего окна
        w - размер окна
        """

        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("Основание должно быть целым числом")

        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError("Показатель должен быть целым числом")

        if not isinstance(modulus, int) or isinstance(modulus, bool):
            raise TypeError("Модуль должен быть целым числом")

        if not isinstance(w, int) or isinstance(w, bool):
            raise TypeError("Размер окна должен быть целым числом")

        if modulus <= 0:
            raise ValueError("Модуль должен быть положительным")

        if exponent < 0:
            raise ValueError("Показатель не может быть отрицательным")

        if w < 1:
            raise ValueError("Размер окна должен быть не меньше 1")

        # Сброс статистики
        self.stats.reset()
        self.last_trace = []

        self.precomputation_stats = {
            "squarings": 0,
            "multiplications": 0,
            "redc": 0,
        }

        self.execution_stats = {
            "squarings": 0,
            "multiplications": 0,
            "redc": 0,
        }

        # Обработка особых случаев
        if modulus == 1:
            return 0

        if exponent == 0:
            return 1 % modulus

        # Подготовка
        base %= modulus

        binary_exponent = bin(exponent)[2:]

        if trace:
            self.last_trace.append({
                "stage": "preparation",
                "base": base,
                "exponent": exponent,
                "binary_exponent": binary_exponent,
                "window_size": w,
                "modulus": modulus,
            })

        # Предвычисление нечётных степеней
        # table[1] = a
        # table[3] = a^3
        # table[5] = a^5
        cache_key = (
            "sliding_window",
            base,
            modulus,
            w,
            "standard"
        )

        table = cache.get(cache_key) if cache is not None else None

        if table is not None:

            if trace:
                self.last_trace.append({
                    "stage": "cache_hit",
                    "algorithm": "sliding_window",
                    "cache_key": cache_key,
                })

        else:

            if trace:
                self.last_trace.append({
                    "stage": "cache_miss",
                    "algorithm": "sliding_window",
                    "cache_key": cache_key,
                })

            table = {
                1: base
            }

            if w > 1:

                base_squared = (base * base) % modulus

                self.stats.squarings += 1
                self.precomputation_stats["squarings"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "precomputation_square",
                        "power": 2,
                        "value": base_squared,
                    })

                for odd in range(3, 2 ** w, 2):

                    table[odd] = (
                        table[odd - 2] * base_squared
                    ) % modulus

                    self.stats.multiplications += 1
                    self.precomputation_stats["multiplications"] += 1

                    if trace:
                        self.last_trace.append({
                            "stage": "precomputation",
                            "power": odd,
                            "value": table[odd],
                        })

            if cache is not None:
                cache.put(cache_key, table)


        # Основное вычисление
        accumulator = 1
        i = 0
        binary_length = len(binary_exponent)

        while i < binary_length:

            # Если текущий бит равен 0,
            # то выполняем одно возведение в квадрат

            if binary_exponent[i] == "0":

                accumulator = (
                    accumulator * accumulator
                ) % modulus

                self.stats.squarings += 1
                self.execution_stats["squarings"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "zero_bit",
                        "bit_index": i,
                        "accumulator": accumulator,
                    })

                i += 1
                continue

            # Формирование окна
            j = min(i + w, binary_length)

            while binary_exponent[j - 1] == "0":
                j -= 1

            window = binary_exponent[i:j]
            window_length = len(window)
            window_value = int(window, 2)

            if trace:
                self.last_trace.append({
                    "stage": "window",
                    "start": i,
                    "end": j,
                    "bits": window,
                    "value": window_value,
                    "length": window_length,
                })

            # Первое окно
            # Инициализация аккумулятора
            if i == 0:

                accumulator = table[window_value]

                if trace:
                    self.last_trace.append({
                        "stage": "initialization",
                        "window": window,
                        "accumulator": accumulator,
                    })

                i = j
                continue

            # Возведение аккумулятора
            # в квадрат window_length раз
            for square_index in range(window_length):

                accumulator = (
                    accumulator * accumulator
                ) % modulus

                self.stats.squarings += 1
                self.execution_stats["squarings"] += 1

                if trace:
                    self.last_trace.append({
                        "stage": "squaring",
                        "window": window,
                        "square_index": square_index + 1,
                        "accumulator": accumulator,
                    })

            # Умножение на предвычисленную степень
            accumulator = (
                accumulator * table[window_value]
            ) % modulus

            self.stats.multiplications += 1
            self.execution_stats["multiplications"] += 1

            if trace:
                self.last_trace.append({
                    "stage": "multiplication",
                    "window": window,
                    "power": window_value,
                    "accumulator": accumulator,
                })

            # Переход к следующему биту
            i = j

        if trace:
            self.last_trace.append({
                "stage": "result",
                "result": accumulator,
            })

        return accumulator
