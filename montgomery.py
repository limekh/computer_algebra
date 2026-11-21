
from dataclasses import dataclass


@dataclass
class MontgomeryStats:
    redc: int = 0
    multiplications: int = 0
    squarings: int = 0

    def reset(self):
        self.redc = 0
        self.multiplications = 0
        self.squarings = 0


class MontgomeryContext:
    """
    Контекст арифметики Монтгомери для нечётного модуля N

    R = 2^s > N
    N' = -N^(-1) mod R

    Все операции умножения выполняются в представлении Монтгомери
    """

    def __init__(self, modulus: int):
        if not isinstance(modulus, int) or isinstance(modulus, bool):
            raise TypeError("Модуль должен быть целым числом")

        if modulus <= 0:
            raise ValueError("Модуль должен быть положительным")

        if modulus % 2 == 0:
            raise ValueError("Метод Монтгомери требует нечётный модуль")

        self.N = modulus

        # R = 2^s > N
        self.s = max(1, modulus.bit_length())
        self.R = 1 << self.s

        # Маска для получения остатка по модулю R
        self.R_mask = self.R - 1

        # N' = -N^(-1) mod R
        n_inverse = self._mod_inverse(self.N, self.R)
        self.N_prime = (-n_inverse) & self.R_mask

        # R mod N и R^2 mod N
        self.R_mod_N = self.R % self.N
        self.R2_mod_N = (self.R * self.R) % self.N

        self.stats = MontgomeryStats()

        # Последняя трассировка REDC
        self.last_trace = {}

        self.last_power_trace = []

    @staticmethod
    def _extended_gcd(a: int, b: int):
        """Расширенный алгоритм Евклида"""

        old_r, r = a, b
        old_s, s = 1, 0
        old_t, t = 0, 1

        while r != 0:
            q = old_r // r

            old_r, r = r, old_r - q * r
            old_s, s = s, old_s - q * s
            old_t, t = t, old_t - q * t

        return old_r, old_s, old_t

    @classmethod
    def _mod_inverse(cls, a: int, modulus: int) -> int:
        """Вычисление обратного элемента через алгоритм Евклида"""

        gcd, x, _ = cls._extended_gcd(a, modulus)

        if gcd != 1:
            raise ValueError("Обратный элемент не существует")

        return x % modulus

    def redc(self, T: int, trace: bool = False) -> int:
        """
        Редукция Монтгомери

        Требование: 0 <= T < R * N

        REDC(T) = (T * R^(-1)) mod N
        """

        if not isinstance(T, int) or isinstance(T, bool):
            raise TypeError("T должно быть целым числом")

        if not 0 <= T < self.R * self.N:
            raise ValueError("T должно удовлетворять условию 0 <= T < R*N")

        self.stats.redc += 1

        # m = (T mod R) * N' mod R
        m = ((T & self.R_mask) * self.N_prime) & self.R_mask

        # t = (T + m*N) / R
        numerator = T + m * self.N
        t = numerator >> self.s

        # Коррекция результата
        corrected = t >= self.N

        result = t - self.N if corrected else t

        if trace:
            self.last_trace = {
                "T": T,
                "m": m,
                "numerator": numerator,
                "t_before_correction": t,
                "correction_applied": corrected,
                "result": result,
            }

        return result

    def to_montgomery(self, value: int) -> int:
        """Перевод числа в представление Монтгомери"""

        value %= self.N

        # REDC(value * R^2 mod N) = value * R mod N
        return self.redc(value * self.R2_mod_N)

    def from_montgomery(self, value: int) -> int:
        """Возврат из представления Монтгомери"""

        self._validate_residue(value)

        return self.redc(value)

    def _validate_residue(self, value: int):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("Число должно быть целым")

        if not 0 <= value < self.N:
            raise ValueError("Число должно находиться в диапазоне [0, N)")

    def multiply(self, a: int, b: int, trace: bool = False) -> int:
        """
        Умножение двух чисел в представлении Монтгомери
        """

        self._validate_residue(a)
        self._validate_residue(b)

        self.stats.multiplications += 1

        return self.redc(a * b, trace=trace)

    def square(self, a: int, trace: bool = False) -> int:
        """Возведение числа в квадрат в представлении Монтгомери"""

        self._validate_residue(a)

        self.stats.squarings += 1

        return self.redc(a * a, trace=trace)

    def multiply_standard(self, a: int, b: int) -> int:
        """Обычное модульное умножение для сравнения"""

        return (a * b) % self.N

    def reset_stats(self):
        """Сброс счётчиков операций"""

        self.stats.reset()

    def parameters(self) -> dict:
        """Возвращение параметров алгоритма"""

        return {
            "N": self.N,
            "R": self.R,
            "s": self.s,
            "N_prime": self.N_prime,
            "R_mod_N": self.R_mod_N,
            "R2_mod_N": self.R2_mod_N,
        }

    def pow_montgomery(self, base: int, exponent: int,
                   trace: bool = False) -> int:
        """
        Возведение в степень методом Монтгомери
        """

        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("Основание должно быть целым числом")

        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError("Показатель должен быть целым числом")

        if exponent < 0:
            raise ValueError("Показатель не может быть отрицательным")

        self.last_power_trace = []

        # Особый случай: N = 1
        if self.N == 1:
            return 0

        # Особый случай: x = 0
        if exponent == 0:
            return 1 % self.N

        # 1. Подготовка
        base %= self.N

        base_mont = self.to_montgomery(base)

        # Двоичное представление показателя
        binary_exponent = bin(exponent)[2:]
        print(f"\nBINARY EXP: {binary_exponent}\n")

        if trace:
            self.last_power_trace.append({
                "stage": "preparation",
                "base": base,
                "exponent": exponent,
                "binary_exponent": binary_exponent,
                "base_montgomery": base_mont,
                "R": self.R,
                "N_prime": self.N_prime,
            })

        # 2. Инициализация аккумулятора
        accumulator = base_mont

        if trace:
            self.last_power_trace.append({
                "stage": "initialization",
                "accumulator": accumulator,
            })

        # 3. Обработка битов от старшего к младшему
        # Старший бит уже учтён инициализацией
        for i in range(1, len(binary_exponent)):

            bit = int(binary_exponent[i])

            # Возведение аккумулятора в квадрат:
            # acc = M(acc, acc)
            accumulator = self.square(accumulator, trace=trace)

            if trace:
                self.last_power_trace.append({
                    "stage": "squaring",
                    "bit_index": len(binary_exponent) - 1 - i,
                    "bit": bit,
                    "accumulator": accumulator,
                    "redc": self.last_trace.copy(),
                })

            # Если текущий бит равен 1:
            # acc = M(acc, base_mont)
            if bit == 1:

                accumulator = self.multiply(
                    accumulator,
                    base_mont,
                    trace=trace
                )

                if trace:
                    self.last_power_trace.append({
                        "stage": "multiplication",
                        "bit_index": len(binary_exponent) - 1 - i,
                        "bit": bit,
                        "accumulator": accumulator,
                        "redc": self.last_trace.copy(),
                    })

        # 4. Возвращение к обычному представлению.
        # M(acc, 1) = REDC(acc).
        result = self.redc(accumulator, trace=trace)

        if trace:
            self.last_power_trace.append({
                "stage": "conversion",
                "accumulator": accumulator,
                "redc": self.last_trace.copy(),
                "result": result,
            })

        return result
