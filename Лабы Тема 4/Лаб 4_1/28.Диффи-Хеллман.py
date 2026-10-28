# ============================================================
# БЛОК K: ОБМЕН КЛЮЧАМИ
# Лаб 2_2 (задание 28) — Обмен ключами по Диффи-Хеллману
# Источник: ЛАБКРИПТ_2022, стр. 40
# ============================================================
#
# АЛГОРИТМ (по методичке):
#   Публичные параметры: n — большое простое, a (1 < a < n)
#   Секретные ключи:     K_A, K_B — случайные числа из [2, n-1]
#   Открытые ключи:      Y_A = a^K_A mod n,  Y_B = a^K_B mod n
#   Обмен:               Y_A и Y_B передаются по открытому каналу
#   Общий секрет:        K_A: K = Y_B^K_A mod n
#                        K_B: K = Y_A^K_B mod n
#   Проверка:            K_A == K_B (оба должны совпадать)
#
# ДОКАЗАТЕЛЬСТВО:
#   A: Y_B^K_A mod n = (a^K_B)^K_A mod n = a^(K_B*K_A) mod n = K
#   B: Y_A^K_B mod n = (a^K_A)^K_B mod n = a^(K_A*K_B) mod n = K
# ============================================================

import random
import sys


# ─────────────────────────────────────────────
#  Математические вспомогательные функции
# ─────────────────────────────────────────────

def mod_pow(base, exp, mod):
    """Быстрое возведение в степень по модулю (алгоритм «двоичного возведения»)."""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


def is_prime(n):
    """Детерминированная проверка простоты методом пробных делений."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def miller_rabin(n, k=10):
    """Тест Миллера–Рабина для больших чисел (вероятностный, k раундов)."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    # Представляем n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=512):
    """Генерация случайного простого числа заданной битности (тест Миллера–Рабина)."""
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1  # нечётное, старший бит = 1
        if miller_rabin(candidate):
            return candidate


def find_primitive_root(p):
    """
    Находит первообразный корень (примитивный корень) по модулю простого p.
    Для простого p φ(p) = p-1. Перебираем кандидатов от 2.
    """
    phi = p - 1
    # Факторизация phi
    factors = set()
    temp = phi
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.add(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    # Проверяем кандидатов
    for g in range(2, p):
        ok = True
        for factor in factors:
            if mod_pow(g, phi // factor, p) == 1:
                ok = False
                break
        if ok:
            return g
    return -1  # не найден (не должно случиться для простого p)


# ─────────────────────────────────────────────
#  Класс протокола Диффи-Хеллмана
# ─────────────────────────────────────────────

class DiffieHellman:
    """
    Протокол обмена ключами Диффи–Хеллмана.

    Публичные параметры:  n (простое), a (примитивный корень по модулю n)
    Секретные ключи:      K_A, K_B ∈ [2, n-1]
    Открытые ключи:       Y_A = a^K_A mod n,  Y_B = a^K_B mod n
    Общий секрет:         K = Y_B^K_A mod n  =  Y_A^K_B mod n
    """

    def __init__(self):
        self.n = None      # публичный модуль (большое простое)
        self.a = None      # публичный генератор (примитивный корень)
        self.K_A = None    # секретный ключ пользователя A
        self.K_B = None    # секретный ключ виртуального пользователя B
        self.Y_A = None    # открытый ключ A
        self.Y_B = None    # открытый ключ B
        self.shared_K_A = None   # общий секрет, вычисленный стороной A
        self.shared_K_B = None   # общий секрет, вычисленный стороной B

    # ── Установка публичных параметров ──────────────────────

    def set_params(self, n, a):
        """Устанавливает публичные параметры n и a с проверками."""
        if not is_prime(n) and not miller_rabin(n):
            print("  Ошибка: n должно быть простым числом!")
            return False
        if not (1 < a < n):
            print(f"  Ошибка: a должно быть в диапазоне (1 < a < n={n})!")
            return False
        self.n = n
        self.a = a
        # Сброс предыдущих ключей
        self.K_A = self.K_B = self.Y_A = self.Y_B = None
        self.shared_K_A = self.shared_K_B = None
        print(f"\n  Публичные параметры установлены:")
        print(f"    n = {n}")
        print(f"    a = {a}  (генератор)")
        return True

    def auto_generate_params(self, bits=64):
        """Автоматически генерирует большое простое n и примитивный корень a."""
        print(f"\n  Генерация простого числа ({bits} бит)...")
        n = generate_prime(bits)
        print(f"  Найдено простое n = {n}")
        print(f"  Поиск примитивного корня по модулю n...")
        a = find_primitive_root(n)
        if a == -1:
            print("  Ошибка: не удалось найти примитивный корень.")
            return False
        print(f"  Найден примитивный корень a = {a}")
        self.n = n
        self.a = a
        self.K_A = self.K_B = self.Y_A = self.Y_B = None
        self.shared_K_A = self.shared_K_B = None
        return True

    # ── Шаг 1: Выбор секретных ключей ───────────────────────

    def set_secret_key_A(self, K_A):
        """Задаёт секретный ключ пользователя A."""
        if self.n is None:
            print("  Ошибка: сначала установите публичные параметры!")
            return False
        if not (2 <= K_A <= self.n - 1):
            print(f"  Ошибка: K_A должно быть в диапазоне [2, n-1 = {self.n - 1}]!")
            return False
        self.K_A = K_A
        print(f"  Секретный ключ A: K_A = {K_A}")
        return True

    def auto_secret_key_B(self):
        """Виртуальный пользователь B сам выбирает случайный секретный ключ."""
        if self.n is None:
            print("  Ошибка: сначала установите публичные параметры!")
            return False
        self.K_B = random.randint(2, self.n - 1)
        print(f"  Виртуальный пользователь B выбрал: K_B = {self.K_B}  (СЕКРЕТ — известен только B)")
        return True

    def set_secret_key_B(self, K_B):
        """Задаёт секретный ключ пользователя B, введённый вручную."""
        if self.n is None:
            print("  Ошибка: сначала установите публичные параметры!")
            return False
        if not (2 <= K_B <= self.n - 1):
            print(f"  Ошибка: K_B должно быть в диапазоне [2, n-1 = {self.n - 1}]!")
            return False
        self.K_B = K_B
        print(f"  Секретный ключ B: K_B = {K_B}")
        return True

    # ── Шаг 2: Вычисление открытых ключей ───────────────────

    def compute_public_keys(self):
        """
        Шаг 2 алгоритма:
          Y_A = a^K_A mod n
          Y_B = a^K_B mod n
        """
        if None in (self.n, self.a, self.K_A, self.K_B):
            print("  Ошибка: не все параметры установлены!")
            return False
        self.Y_A = mod_pow(self.a, self.K_A, self.n)
        self.Y_B = mod_pow(self.a, self.K_B, self.n)
        print(f"\n  Открытые ключи (передаются по открытому каналу):")
        print(f"    Y_A = a^K_A mod n = {self.a}^{self.K_A} mod {self.n} = {self.Y_A}")
        print(f"    Y_B = a^K_B mod n = {self.a}^{self.K_B} mod {self.n} = {self.Y_B}")
        return True

    # ── Шаг 3: Вычисление общего секрета ────────────────────

    def compute_shared_secret(self):
        """
        Шаг 3 алгоритма:
          K_A: K = Y_B^K_A mod n
          K_B: K = Y_A^K_B mod n
          Проверка: K_A == K_B
        """
        if None in (self.Y_A, self.Y_B, self.K_A, self.K_B):
            print("  Ошибка: сначала вычислите открытые ключи!")
            return False

        self.shared_K_A = mod_pow(self.Y_B, self.K_A, self.n)
        self.shared_K_B = mod_pow(self.Y_A, self.K_B, self.n)

        print(f"\n  Вычисление общего секрета:")
        print(f"    A: K = Y_B^K_A mod n = {self.Y_B}^{self.K_A} mod {self.n} = {self.shared_K_A}")
        print(f"    B: K = Y_A^K_B mod n = {self.Y_A}^{self.K_B} mod {self.n} = {self.shared_K_B}")

        if self.shared_K_A == self.shared_K_B:
            print(f"\n  ✓ ПРОВЕРКА ПРОЙДЕНА: K_A = K_B = {self.shared_K_A}")
            print(f"    Общий секретный ключ успешно выработан!")
        else:
            print(f"\n  ✗ ОШИБКА: K_A ≠ K_B  ({self.shared_K_A} ≠ {self.shared_K_B})")
        return self.shared_K_A == self.shared_K_B

    # ── Полная демонстрация протокола ────────────────────────

    def full_demo(self):
        """Полная пошаговая демонстрация протокола Диффи-Хеллмана."""
        sep = "─" * 60
        print(f"\n{sep}")
        print("  ПРОТОКОЛ ОБМЕНА КЛЮЧАМИ ДИФФИ-ХЕЛЛМАНА")
        print(f"  Источник: ЛАБКРИПТ_2022, Блок K, Задание 28")
        print(sep)

        print("\n  Шаг 1. Публичные параметры (известны всем):")
        print(f"    n = {self.n}  (простое число)")
        print(f"    a = {self.a}  (1 < a < n, примитивный корень)")

        print("\n  Шаг 2. Выбор секретных ключей:")
        print(f"    Пользователь A выбирает K_A = {self.K_A}  (из интервала [2, n-1])")
        print(f"    Пользователь B выбирает K_B = {self.K_B}  (из интервала [2, n-1])")

        print("\n  Шаг 3. Вычисление открытых ключей:")
        self.compute_public_keys()

        print("\n  Шаг 4. Обмен открытыми ключами по открытому каналу:")
        print(f"    A → B: Y_A = {self.Y_A}")
        print(f"    B → A: Y_B = {self.Y_B}")

        print("\n  Шаг 5. Независимое вычисление общего секрета:")
        ok = self.compute_shared_secret()

        print(f"\n{sep}")
        if ok:
            print(f"  ИТОГ: Общий секретный ключ K = {self.shared_K_A}")
        else:
            print("  ИТОГ: Ошибка в протоколе!")
        print(sep)
        return ok


# ─────────────────────────────────────────────
#  Меню
# ─────────────────────────────────────────────

def print_menu(dh):
    """Выводит текущее меню с состоянием."""
    print("\n" + "=" * 60)
    print("  БЛОК K: ОБМЕН КЛЮЧАМИ (Задание 28 — Диффи-Хеллман)")
    print("=" * 60)

    # Текущее состояние параметров
    if dh.n:
        print(f"  n = {dh.n}  |  a = {dh.a}")
    else:
        print("  Параметры не установлены")
    if dh.K_A:
        print(f"  K_A = {dh.K_A}  |  K_B = {'установлен' if dh.K_B else 'не установлен'}")
    if dh.shared_K_A:
        print(f"  Общий ключ K = {dh.shared_K_A}")

    print()
    print("  1 — Ввести публичные параметры (n, a) вручную")
    print("  2 — Авто-генерация параметров (простое n и генератор a)")
    print("  3 — Ввести секретный ключ A (K_A) вручную")
    print("  4 — Ввести секретный ключ B (K_B) вручную")
    print("  5 — Вычислить открытые ключи Y_A и Y_B")
    print("  6 — Вычислить общий секрет и проверить протокол")
    print("  7 — Полная демонстрация (авто, от начала до конца)")
    print("  8 — Пример из методички (малые числа)")
    print("  0 — Выход")
    print()


def demo_textbook(dh):
    """
    Демонстрация с малыми числами по образцу методички.
    Используем простое n=23, генератор a=5 — классический учебный пример.
    """
    print("\n" + "─" * 60)
    print("  ПРИМЕР ПО МЕТОДИЧКЕ (малые числа)")
    print("─" * 60)
    print("  Публичные параметры: n = 23 (простое), a = 5")
    print("  Пользователь A выбирает K_A = 6")
    print("  Пользователь B выбирает K_B = 15")

    dh.n = 23
    dh.a = 5
    dh.K_A = 6
    dh.K_B = 15
    dh.Y_A = None
    dh.Y_B = None
    dh.shared_K_A = None
    dh.shared_K_B = None

    print("\n  Открытые ключи:")
    dh.compute_public_keys()
    print("\n  Общий секрет:")
    dh.compute_shared_secret()


def main():
    dh = DiffieHellman()

    while True:
        print_menu(dh)
        choice = input("  Ваш выбор: ").strip()

        if choice == "1":
            try:
                n = int(input("  Введите простое число n: "))
                a = int(input("  Введите генератор a (1 < a < n): "))
                dh.set_params(n, a)
            except ValueError:
                print("  Ошибка: введите целые числа.")

        elif choice == "2":
            try:
                bits = int(input("  Битность n (рекомендуется 64-128 для демо, 512+ для практики) [64]: ").strip() or "64")
                dh.auto_generate_params(bits)
            except ValueError:
                print("  Ошибка: введите целое число.")

        elif choice == "3":
            if dh.n is None:
                print("  Ошибка: сначала установите параметры (п.1 или п.2).")
            else:
                try:
                    K_A = int(input(f"  Введите секретный ключ K_A (из [2, {dh.n - 1}]): "))
                    dh.set_secret_key_A(K_A)
                except ValueError:
                    print("  Ошибка: введите целое число.")

        elif choice == "4":
            if dh.n is None:
                print("  Ошибка: сначала установите параметры (п.1 или п.2).")
            else:
                try:
                    K_B = int(input(f"  Введите секретный ключ K_B (из [2, {dh.n - 1}]): "))
                    dh.set_secret_key_B(K_B)
                except ValueError:
                    print("  Ошибка: введите целое число.")

        elif choice == "5":
            dh.compute_public_keys()

        elif choice == "6":
            dh.compute_shared_secret()

        elif choice == "7":
            # Полная авто-демонстрация
            try:
                bits = int(input("  Битность n [64]: ").strip() or "64")
            except ValueError:
                bits = 64
            dh.auto_generate_params(bits)
            try:
                K_A = int(input(f"  Введите свой секретный ключ K_A (из [2, {dh.n-1}]): "))
                dh.set_secret_key_A(K_A)
            except ValueError:
                dh.K_A = random.randint(2, dh.n - 1)
                print(f"  Для A случайно выбран K_A = {dh.K_A}")
            dh.auto_secret_key_B()
            dh.full_demo()

        elif choice == "8":
            demo_textbook(dh)

        elif choice == "0":
            print("  Выход.")
            break

        else:
            print("  Неверный выбор.")

        input("\n  Нажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
