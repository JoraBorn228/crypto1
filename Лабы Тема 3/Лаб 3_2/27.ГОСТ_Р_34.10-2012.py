"""
Лабораторная работа 3_2
Алгоритм 27: ЭЦП по ГОСТ Р 34.10-2012
Вариант: "Леопард не может изменить своих пятен"
"""
import random

СООБЩЕНИЕ = "Леопард не может изменить своих пятен"

# Кривая y² ≡ x³ + 4x + 1 (mod 29)
# Точка (0,1): 1²=1, 0+0+1=1 (mod 29) ✓
# Порядок группы = 31 (простое), генератор P=(0,1)
# Проверка: 31·P = O, 30·P = (0,28) ≠ O ✓


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
                return None                        # точка на бесконечности
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


CURVE = EllipticCurve(p=29, a=4, b=1)
P_BASE = (0, 1)
Q_ORDER = 31


def hash_func(message, q):
    """Квадратичная свёртка: h_i = (h_{i-1} + ord(c_i))^2 mod q"""
    h = 1
    for ch in message:
        h = (h + ord(ch)) ** 2 % q
    return h if h != 0 else 1


def keygen(curve, P, q):
    d = random.randint(1, q - 1)          # закрытый ключ
    Q = curve.mul(d, P)                    # открытый ключ Q = d·P
    return d, Q


def sign(message, curve, P, q, d, k=None):
    alpha = hash_func(message, q)
    e = alpha % q or 1
    if not 0 < d < q:
        raise ValueError(f"Закрытый ключ d должен быть в диапазоне 1..{q - 1}.")
    if k is not None:
        if not 0 < k < q:
            raise ValueError(f"Одноразовый ключ k должен быть в диапазоне 1..{q - 1}.")
        C = curve.mul(k, P)
        if C is None:
            raise ValueError("Выбранный k дал точку на бесконечности; введите другое k.")
        r = C[0] % q
        s = (r * d + k * e) % q
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
        s = (r * d + k * e) % q
        if s == 0:
            continue
        return r, s, e, k


def verify(message, r, s, curve, P, Q_pub, q):
    if not (0 < r < q and 0 < s < q):
        return False
    alpha = hash_func(message, q)
    e = alpha % q or 1
    v = pow(e, q - 2, q)             # e^{-1} mod q
    z1 = s * v % q
    z2 = (-r * v) % q
    C = curve.add(curve.mul(z1, P), curve.mul(z2, Q_pub))
    if C is None:
        return False
    return C[0] % q == r


def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-2012  —  Цифровая подпись (эллиптические кривые)")
    print("=" * 60)
    print(f"Кривая     : y² ≡ x³ + {CURVE.a}x + {CURVE.b}  (mod {CURVE.p})")
    print(f"Генератор  : P = {P_BASE}")
    print(f"Порядок    : q = {Q_ORDER}")
    print("Учебные малые параметры: это демонстрация алгоритма, не промышленный профиль ГОСТ.")
    while True:
        print("\n1 - Создать подпись (ввести сообщение, d и одноразовый k)")
        print("2 - Проверить подпись (ввести сообщение, r, s и открытый ключ Q)")
        print("0 - Выход")
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            break
        try:
            if choice == "1":
                message = input("Введите сообщение: ")
                if not message:
                    raise ValueError("Сообщение не должно быть пустым.")
                d = int(input(f"Введите закрытый ключ d (1..{Q_ORDER - 1}): "))
                k = int(input(f"Введите одноразовый ключ k (1..{Q_ORDER - 1}): "))
                if not (0 < d < Q_ORDER):
                    raise ValueError(f"d должен быть в диапазоне 1..{Q_ORDER - 1}.")
                Q_pub = CURVE.mul(d, P_BASE)
                r, s, e, _ = sign(message, CURVE, P_BASE, Q_ORDER, d, k)
                print(f"Хэш e = {e}")
                print(f"Открытый ключ Q = {Q_pub}")
                print(f"Подпись (r, s) = ({r}, {s})")
                print(f"Проверка созданной подписи: {'ВЕРНА' if verify(message, r, s, CURVE, P_BASE, Q_pub, Q_ORDER) else 'НЕ ВЕРНА'}")
            elif choice == "2":
                message = input("Введите исходное сообщение: ")
                r = int(input("Введите r: "))
                s = int(input("Введите s: "))
                qx = int(input("Введите координату Qx: "))
                qy = int(input("Введите координату Qy: "))
                Q_pub = (qx, qy)
                if not CURVE.is_on_curve(Q_pub):
                    raise ValueError("Открытый ключ Q не принадлежит заданной эллиптической кривой.")
                valid = verify(message, r, s, CURVE, P_BASE, Q_pub, Q_ORDER)
                print(f"Результат проверки: {'ПОДПИСЬ ВЕРНА' if valid else 'ПОДПИСЬ НЕВЕРНА'}")
            else:
                print("Выберите 0, 1 или 2.")
        except ValueError as exc:
            print(f"Ошибка ввода: {exc}")


if __name__ == "__main__":
    main()
