"""
Лабораторная работа 3_2
Алгоритм 27: ЭЦП по ГОСТ Р 34.10-2012
Вариант: "Леопард не может изменить своих пятен"

Источник: ЛАБКРИПТ_2022, Блок J, стр. 37-39
Задание: "PDF/Задание по ГОСТ Р 34.10-2012..pdf"

Параметры из методички (пример):
  Кривая E_p(a,b): y² ≡ x³ + x + 1 (mod 11)
  a = 1, b = 1, p = 11
  Порядок подгруппы q = 7
  Генератор G = (0, 1)

Хэш-функция квадратичной свёртки (h_0 = 0):
  h_i = (h_{i-1} + M_i)² mod q
  где M_i — коды (ord) символов сообщения

Подпись (отправитель):
  1. Выбрать секретный ключ 0 < x_A < q
  2. Вычислить Y_A = x_A * G (открытый ключ)
  3. Вычислить e = h(сообщение) mod q, если e=0 → e=1
  4. Выбрать случайное 0 < k < q
  5. Вычислить C = k * G, r = x_C mod q
  6. s = (k * e + r * x_A) mod q
  7. Подпись: (r, s)

Проверка (получатель):
  1. Вычислить e = h(сообщение) mod q, если e=0 → e=1
  2. Проверить 0 < r < q и 0 < s < q
  3. v = e⁻¹ mod q
  4. z₁ = s * v mod q
  5. z₂ = -r * v mod q
  6. C' = z₁*G + z₂*Y_A
  7. r' = x_{C'} mod q; если r' = r — подпись верна
"""
import random
from math import isqrt

# ─────────────────────────────────────────────
#  Эллиптическая кривая
# ─────────────────────────────────────────────

class EllipticCurve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

    def is_on_curve(self, point):
        if point is None:
            return True
        x, y = point
        return (y * y - x ** 3 - self.a * x - self.b) % self.p == 0

    def neg(self, P):
        if P is None:
            return None
        return P[0], (-P[1]) % self.p

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        p = self.p
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None  # точка на бесконечности
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return x3, y3

    def mul(self, k, P):
        """Скалярное умножение методом двоичного разложения."""
        result = None
        addend = P
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result


def point_order(curve, P):
    """Вычисляет порядок точки P перебором кратных P.

    Для кривой над простым полем порядок группы точек не превосходит
    p + 1 + 2*sqrt(p) (граница Хассе), поэтому перебор имеет верхнюю границу.
    """
    if curve.p <= 1:
        raise ValueError("Модуль p должен быть больше 1.")
    if P is None or not curve.is_on_curve(P):
        raise ValueError("Точка G должна лежать на заданной кривой.")

    max_order = curve.p + 1 + isqrt(4 * curve.p)
    multiple = None
    for order in range(1, max_order + 1):
        multiple = curve.add(multiple, P)
        if multiple is None:
            return order
    raise ValueError("Не удалось вычислить порядок G; проверьте параметры кривой.")


# ─────────────────────────────────────────────
#  Хэш-функция квадратичной свёртки (ЛАБКРИПТ_2022, стр. 1)
#  h_0 = 0
#  h_i = (h_{i-1} + M_i)² mod p
# ─────────────────────────────────────────────

def hash_func(message: str, q: int) -> int:
    """
    Упрощённая хэш-функция квадратичной свёртки по методичке:
      h_0 = 0
      h_i = (h_{i-1} + ord(M_i))² mod q
    Если h = 0 — возвращаем 1 (защита от нулевого хэша).
    """
    h = 0
    for ch in message:
        h = (h + ord(ch)) ** 2 % q
    return h if h != 0 else 1


# ─────────────────────────────────────────────
#  Генерация ключей
# ─────────────────────────────────────────────

def keygen(curve, P, q):
    d = random.randint(1, q - 1)   # закрытый ключ
    Q = curve.mul(d, P)             # открытый ключ Q = d·P
    return d, Q


# ─────────────────────────────────────────────
#  Создание подписи
# ─────────────────────────────────────────────

def sign(message, curve, P, q, d, k=None):
    e = hash_func(message, q)
    if not 0 < d < q:
        raise ValueError(f"Закрытый ключ d должен быть в диапазоне 1..{q - 1}.")
    if k is not None:
        if not 0 < k < q:
            raise ValueError(f"Одноразовый ключ k должен быть в диапазоне 1..{q - 1}.")
        C = curve.mul(k, P)
        if C is None:
            raise ValueError("Выбранный k дал точку на бесконечности; введите другое k.")
        r = C[0] % q
        s = (k * e + r * d) % q
        if r == 0 or s == 0:
            raise ValueError("Для выбранного k получено r=0 или s=0; введите другое k.")
        return r, s, e, k
    while True:
        k = random.randint(1, q - 1)
        C = curve.mul(k, P)
        if C is None:
            continue
        r = C[0] % q
        if r == 0:
            continue
        s = (k * e + r * d) % q
        if s == 0:
            continue
        return r, s, e, k


# ─────────────────────────────────────────────
#  Проверка подписи
# ─────────────────────────────────────────────

def verify(message, r, s, curve, P, Q_pub, q):
    if not (0 < r < q and 0 < s < q):
        return False
    e = hash_func(message, q)
    v = pow(e, q - 2, q)       # e^{-1} mod q
    z1 = s * v % q
    z2 = (-r * v) % q
    C = curve.add(curve.mul(z1, P), curve.mul(z2, Q_pub))
    if C is None:
        return False
    return C[0] % q == r


# ─────────────────────────────────────────────
#  Главное меню
# ─────────────────────────────────────────────

# Параметры по умолчанию из примера методички (ЛАБКРИПТ_2022, стр. 37)
#   E_p(a,b): y² ≡ x³ + x + 1 (mod 11)
#   a=1, b=1, p=11, q=7, G=(0,1)
DEFAULT_P = 11
DEFAULT_A = 1
DEFAULT_B = 1
DEFAULT_G = (0, 1)
DEFAULT_Q = 7


def print_params(curve, G, q):
    print(f"  Кривая     : y² ≡ x³ + {curve.a}x + {curve.b}  (mod {curve.p})")
    print(f"  Генератор  : G = {G}")
    print(f"  Порядок    : q = {q}")


def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-2012  —  Цифровая подпись (эллиптические кривые)")
    print("=" * 60)
    print("Параметры из методички (ЛАБКРИПТ_2022, Блок J, задание 27):")
    print(f"  Кривая E_p(a,b): y² ≡ x³ + ax + b  (mod p)")
    print(f"  Хэш: h_0=0, h_i=(h_{{i-1}}+ord(M_i))² mod q")
    print()

    # Загружаем параметры по умолчанию
    curve = EllipticCurve(p=DEFAULT_P, a=DEFAULT_A, b=DEFAULT_B)
    P_BASE = DEFAULT_G
    Q_ORDER = DEFAULT_Q

    while True:
        print("\n" + "-" * 60)
        print("Текущие параметры кривой:")
        print_params(curve, P_BASE, Q_ORDER)
        print("-" * 60)
        print("1 — Задать параметры кривой вручную")
        print("2 — Создать подпись")
        print("3 — Проверить подпись")
        print("4 — Показать пример из методички")
        print("0 — Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            break

        try:
            if choice == "1":
                print(f"\nВведите параметры кривой y² ≡ x³ + ax + b (mod p)")
                p = int(input("  p (простое): "))
                a = int(input("  a: "))
                b = int(input("  b: "))
                gx = int(input("  Gx (x-координата генератора): "))
                gy = int(input("  Gy (y-координата генератора): "))
                curve = EllipticCurve(p=p, a=a, b=b)
                P_BASE = (gx, gy)
                if not curve.is_on_curve(P_BASE):
                    print("  ОШИБКА: точка G не лежит на заданной кривой!")
                    # Возвращаем умолчания
                    curve = EllipticCurve(p=DEFAULT_P, a=DEFAULT_A, b=DEFAULT_B)
                    P_BASE = DEFAULT_G
                    Q_ORDER = DEFAULT_Q
                else:
                    Q_ORDER = point_order(curve, P_BASE)
                    print(f"  Порядок точки G вычислен автоматически: q = {Q_ORDER}.")
                    print("  Параметры установлены.")

            elif choice == "2":
                print("\n--- Создание подписи ---")
                message = input("Введите сообщение: ")
                if not message:
                    raise ValueError("Сообщение не должно быть пустым.")
                d = int(input(f"Введите закрытый ключ x_A (1..{Q_ORDER - 1}): "))
                k = int(input(f"Введите одноразовый ключ k (1..{Q_ORDER - 1}): "))
                if not (0 < d < Q_ORDER):
                    raise ValueError(f"x_A должен быть в диапазоне 1..{Q_ORDER - 1}.")
                Q_pub = curve.mul(d, P_BASE)
                r, s, e, _ = sign(message, curve, P_BASE, Q_ORDER, d, k)
                print(f"\nХэш e = {e}")
                print(f"Открытый ключ Y_A = {Q_pub}")
                print(f"Подпись (r, s) = ({r}, {s})")
                ok = verify(message, r, s, curve, P_BASE, Q_pub, Q_ORDER)
                print(f"Проверка созданной подписи: {'ВЕРНА ✓' if ok else 'НЕ ВЕРНА ✗'}")

            elif choice == "3":
                print("\n--- Проверка подписи ---")
                message = input("Введите исходное сообщение: ")
                r = int(input("Введите r: "))
                s = int(input("Введите s: "))
                qx = int(input("Введите координату Y_Ax: "))
                qy = int(input("Введите координату Y_Ay: "))
                Q_pub = (qx, qy)
                if not curve.is_on_curve(Q_pub):
                    raise ValueError("Открытый ключ Y_A не принадлежит заданной эллиптической кривой.")
                valid = verify(message, r, s, curve, P_BASE, Q_pub, Q_ORDER)
                print(f"Результат проверки: {'ПОДПИСЬ ВЕРНА ✓' if valid else 'ПОДПИСЬ НЕВЕРНА ✗'}")

            elif choice == "4":
                print("\n" + "=" * 60)
                print("ПРИМЕР ИЗ МЕТОДИЧКИ (ЛАБКРИПТ_2022, стр. 37)")
                print("=" * 60)
                print("Кривая E_p(a,b): y² ≡ x³ + x + 1 (mod 11)")
                print("a = 1, b = 1, p = 11, q = 7, G = (0, 1)")
                print()
                demo_curve = EllipticCurve(p=11, a=1, b=1)
                demo_G = (0, 1)
                demo_q = 7
                # Пример из PDF: x_A=4, k=5
                demo_xA = 4
                demo_k = 5
                demo_msg = "ДЕВА"  # Из таблицы вариантов для примера
                # Считаем хэш
                demo_e = hash_func(demo_msg, demo_q)
                demo_YA = demo_curve.mul(demo_xA, demo_G)
                demo_C = demo_curve.mul(demo_k, demo_G)
                demo_r = demo_C[0] % demo_q
                demo_s = (demo_k * demo_e + demo_r * demo_xA) % demo_q
                print(f"Сообщение   : {demo_msg!r}")
                print(f"x_A (секрет): {demo_xA}")
                print(f"k (разовый) : {demo_k}")
                print(f"Хэш e       : {demo_e}")
                print(f"Y_A = {demo_xA}·G = {demo_YA}")
                print(f"C = {demo_k}·G = {demo_C}")
                print(f"r = {demo_r}, s = {demo_s}")
                print(f"Подпись (r, s) = ({demo_r}, {demo_s})")
                ok = verify(demo_msg, demo_r, demo_s, demo_curve, demo_G, demo_YA, demo_q)
                print(f"Проверка: {'ВЕРНА ✓' if ok else 'НЕ ВЕРНА ✗'}")
                print("=" * 60)

            else:
                print("Выберите 0, 1, 2, 3 или 4.")

        except ValueError as exc:
            print(f"Ошибка ввода: {exc}")
        except Exception as exc:
            print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
