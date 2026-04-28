"""
Лабораторная работа 3_2
Алгоритм 26: ЭЦП по ГОСТ Р 34.10-94
Вариант: "Леопард не может изменить своих пятен"
"""
import random

СООБЩЕНИЕ = "Леопард не может изменить своих пятен"

# Параметры: p=1019 (простое), q=509 (простое), a=4
# p-1 = 1018 = 2*509, значит q | (p-1)
# a^q mod p = 4^509 mod 1019 = 1 (подгруппа порядка q)
P = 1019
Q = 509
A = 4


def hash_func(message, q):
    """Квадратичная свёртка: h_i = (h_{i-1} + ord(c_i))^2 mod q"""
    h = 1
    for ch in message:
        h = (h + ord(ch)) ** 2 % q
    return h if h != 0 else 1


def keygen(p, q, a):
    x = random.randint(2, q - 1)       # закрытый ключ
    y = pow(a, x, p)                    # открытый ключ y = a^x mod p
    return x, y


def sign(message, p, q, a, x):
    H = hash_func(message, q)
    while True:
        k = random.randint(2, q - 1)
        r = pow(a, k, p) % q
        if r == 0:
            continue
        s = (x * r + k * H) % q
        if s == 0:
            continue
        return r, s, H, k


def verify(message, r, s, p, q, a, y):
    if not (0 < r < q and 0 < s < q):
        return False
    H = hash_func(message, q)
    v = pow(H, q - 2, q)          # H^{-1} mod q (q — простое)
    z1 = s * v % q
    z2 = (q - r) * v % q
    u = pow(a, z1, p) * pow(y, z2, p) % p % q
    return u == r


def main():
    print("=" * 60)
    print("ГОСТ Р 34.10-94  —  Цифровая подпись")
    print("=" * 60)
    print(f"Сообщение : {СООБЩЕНИЕ!r}")
    print(f"Параметры : p={P}, q={Q}, a={A}")

    x, y = keygen(P, Q, A)
    print(f"\nКлючи")
    print(f"  Закрытый x = {x}")
    print(f"  Открытый y = {y}")

    r, s, H, k = sign(СООБЩЕНИЕ, P, Q, A, x)
    print(f"\nПодпись")
    print(f"  Хэш     H = {H}")
    print(f"  Сессион k = {k}")
    print(f"  r         = {r}")
    print(f"  s         = {s}")

    ok = verify(СООБЩЕНИЕ, r, s, P, Q, A, y)
    print(f"\nПроверка подписи : {'ВЕРНА' if ok else 'НЕ ВЕРНА'}")

    print("\n--- Проверка с изменённым сообщением ---")
    ok2 = verify(СООБЩЕНИЕ + "!", r, s, P, Q, A, y)
    print(f"Проверка (изменённое) : {'ВЕРНА' if ok2 else 'НЕ ВЕРНА'}")


if __name__ == "__main__":
    main()
