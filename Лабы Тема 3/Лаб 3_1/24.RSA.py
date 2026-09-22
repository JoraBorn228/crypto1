import random
import os

def is_prime(n: int, k: int = 10) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def prepare_text(message: str) -> str:
    result = ""
    for ch in message.upper():
        if ch == ' ':
            result += "ПРБ"
        elif ch == '.':
            result += "ТЧК"
        else:
            result += ch
    return result

def square_hash(message: str, N: int) -> int:
    alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    h = 0
    print(f"Начальное значение h0 = {h}")
    for ch in message:
        if ch in alphabet:
            code = alphabet.index(ch) + 1
        else:
            continue
        h = (h + code) % N
        h = (h * h) % N
    print(f"Итоговый хеш: {h}")
    return h

class RSASignature:
    def __init__(self):
        self.p = None
        self.q = None
        self.N = None
        self.phi = None
        self.e = None
        self.d = None
        self.keys_ready = False
        self.last_message = ""
        self.last_hash = 0
        self.last_signature = 0

    def set_keys(self, p, q, e):
        if not is_prime(p):
            raise ValueError("p не является простым числом")
        if not is_prime(q):
            raise ValueError("q не является простым числом")
        if p == q:
            raise ValueError("p и q должны быть разными")
        self.p = p
        self.q = q
        self.N = p * q
        self.phi = (p - 1) * (q - 1)

        if not (1 < e < self.phi):
            raise ValueError("e должен быть в диапазоне 1 < e < ф(N)")
        if gcd(e, self.phi) != 1:
            raise ValueError("e и ф(N) не взаимно просты")
        self.e = e

        self.d = mod_inverse(self.e, self.phi)

        if self.e == self.d:
            raise ValueError("Открытый и секретный ключи совпадают")
        if self.N <= 32:
            raise ValueError(f"Модуль N = {self.N} должен быть больше 32")

        self.keys_ready = True
        print("\nКлючи установлены")
        print(f"p = {p}, q = {q}")
        print(f"N = {self.N}")
        print(f"ф(N) = {self.phi}")
        print(f"Открытый ключ e = {e}")
        print(f"Секретный ключ d = {self.d}")

    def sign(self, message):
        if not self.keys_ready:
            raise RuntimeError("Ключи не установлены")
        prepared = prepare_text(message)
        h = square_hash(prepared, self.N)
        signature = pow(h, self.d, self.N)
        self.last_message = message
        self.last_hash = h
        self.last_signature = signature
        print(f"\nПодпись = {h}^{self.d} mod {self.N} = {signature}")
        return signature

    def verify(self):
        if not self.keys_ready:
            raise RuntimeError("Ключи не установлены")
        if not self.last_message:
            raise RuntimeError("Нет подписанного сообщения")
        prepared = prepare_text(self.last_message)
        h = square_hash(prepared, self.N)
        decrypted = pow(self.last_signature, self.e, self.N)
        print(f"\nПроверка подписи")
        print(f"Сообщение: {self.last_message}")
        print(f"Хэш сообщения (число): {h}")
        print(f"Подпись: {self.last_signature}")
        print(f"Вычисляем (подпись)^e mod N = {decrypted}")
        print(f"Сравниваем с хэшем: {h} == {decrypted} => {h == decrypted}")
        return h == decrypted

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    rsa = RSASignature()
    while True:
        clear_screen()
        print("\nЦИФРОВАЯ ПОДПИСЬ RSA")
        print("1. Ввести ключи (p, q, e)")
        print("2. Подписать сообщение")
        print("3. Проверить подпись")
        print("4. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            try:
                p = int(input("Введите простое число p: "))
                q = int(input("Введите простое число q: "))
                e = int(input("Введите открытый ключ e: "))
                rsa.set_keys(p, q, e)
            except Exception as ex:
                print(f"Ошибка: {ex}")

        elif choice == '2':
            if not rsa.keys_ready:
                print("Сначала установите ключи (пункт 1).")
            else:
                msg = input("Введите сообщение для подписи: ")
                try:
                    rsa.sign(msg)
                except Exception as ex:
                    print(f"Ошибка: {ex}")

        elif choice == '3':
            if not rsa.keys_ready:
                print("Сначала установите ключи (пункт 1).")
            elif not rsa.last_message:
                print("Сначала подпишите сообщение (пункт 2).")
            else:
                try:
                    valid = rsa.verify()
                    if valid:
                        print("\nПОДПИСЬ ВЕРНА")
                    else:
                        print("\nПОДПИСЬ НЕВЕРНА")
                except Exception as ex:
                    print(f"Ошибка: {ex}")

        elif choice == '4':
            print("Программа завершена.")
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
