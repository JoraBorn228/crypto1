import random
import sys

# ---------- Тест Миллера–Рабина ----------
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


# ---------- Хэш-функция квадратичной свертки ----------
def square_hash(message: str, p: int, q: int) -> int:
    alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    prepared = []
    for ch in message.upper():
        if ch == ' ':
            continue
        elif ch == '.':
            prepared.extend(['Т', 'Ч', 'К'])
        else:
            prepared.append(ch)
    h = 0
    for ch in prepared:
        if ch not in alphabet:
            continue
        code = alphabet.index(ch) + 1
        h = (h + code) ** 2 % p
    hm = h % q
    if hm == 0:
        hm = 1
    return hm


# ---------- Генерация всех возможных a для заданных p и q ----------
def generate_possible_a(p: int, q: int) -> list:
    result = []
    for a in range(2, p - 1):
        if pow(a, q, p) == 1:
            result.append(a)
    return result


# ---------- Класс ГОСТ ----------
class Gost341094:
    def __init__(self):
        self.p = None
        self.q = None
        self.a = None
        self.x = None
        self.y = None
        self.params_ready = False
        self.last_message = ""
        self.last_signature = (None, None)
        self.last_hash = None

    def set_params(self, p: int, q: int, a: int, x: int):
        """Устанавливает параметры после проверки."""
        if p <= 32:
            raise ValueError(f"p = {p} должно быть больше 32")
        if not is_prime(p):
            raise ValueError(f"p = {p} не является простым числом")
        if not is_prime(q):
            raise ValueError(f"q = {q} не является простым числом")
        if (p - 1) % q != 0:
            raise ValueError(f"q = {q} не делит (p-1) = {p-1}")
        if not (1 < a < p - 1):
            raise ValueError(f"a = {a} не в диапазоне 1 < a < p-1")
        if pow(a, q, p) != 1:
            raise ValueError(f"a^{q} mod {p} = {pow(a, q, p)} ≠ 1")
        if not (0 < x < q):
            raise ValueError(f"x = {x} не в диапазоне 0 < x < q")

        self.p = p
        self.q = q
        self.a = a
        self.x = x
        self.y = pow(a, x, p)
        self.params_ready = True

        print("\nПараметры приняты.")
        print(f"p = {p}")
        print(f"q = {q}")
        print(f"a = {a}")
        print(f"Секретный ключ x = {x}")
        print(f"Открытый ключ y = a^x mod p = {self.y}")

    def sign(self, message: str):
        if not self.params_ready:
            raise RuntimeError("Сначала установите параметры.")
        q = self.q
        p = self.p
        hm = square_hash(message, p, q)
        self.last_hash = hm
        print(f"\nХэш сообщения (H(m) mod q) = {hm}")

        while True:
            k = random.randint(1, q - 1)
            r = pow(self.a, k, self.p) % q
            if r == 0:
                continue
            s = (self.x * r + k * hm) % q
            break
        self.last_message = message
        self.last_signature = (r, s)
        print(f"\nПодпись для \"{message}\": r = {r}, s = {s}")
        return (r, s)

    def verify(self) -> bool:
        if not self.params_ready:
            raise RuntimeError("Параметры не установлены.")
        if self.last_signature == (None, None):
            raise RuntimeError("Нет подписанного сообщения.")

        r, s = self.last_signature
        message = self.last_message
        p, q, a, y = self.p, self.q, self.a, self.y
        hm = square_hash(message, p, q)
        print(f"\nХэш сообщения (H(m) mod q) = {hm}")

        v = pow(hm, q - 2, q)
        z1 = (s * v) % q
        z2 = ((q - r) % q) * v % q
        u = (pow(a, z1, p) * pow(y, z2, p)) % p % q

        print(f"v = {v}, z1 = {z1}, z2 = {z2}, u = {u}")
        if u == r:
            print("u == r => ПОДПИСЬ ВЕРНА")
            return True
        else:
            print("u != r => ПОДПИСЬ НЕВЕРНА")
            return False

def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")

# ---------- Главное меню ----------
def main():
    gost = Gost341094()

    while True:
        print("ЦИФРОВАЯ ПОДПИСЬ ГОСТ Р 34.10-94")
        print("1. Установить параметры (p, q, a, x)")
        print("2. Подписать сообщение")
        print("3. Проверить подпись")
        print("4. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            try:
                # Ввод p
                p = input_int("Введите простое p (p > 32): ")
                # Ввод q
                q = input_int("Введите простое q (делитель p-1): ")

                # Предварительные проверки (без a)
                if p <= 32:
                    raise ValueError("p должно быть > 32")
                if not is_prime(p):
                    raise ValueError("p не простое")
                if not is_prime(q):
                    raise ValueError("q не простое")
                if (p - 1) % q != 0:
                    raise ValueError("q не делит p-1")

                # Генерация возможных a
                possible_a = generate_possible_a(p, q)
                if not possible_a:
                    raise ValueError("Нет подходящих a для данных p и q.")

                print(f"\nНайдено {len(possible_a)} возможных значений a:")
                print(possible_a)
                print("\nВыберите одно из них (введите число).")
                a = input_int("a = ")
                if a not in possible_a:
                    raise ValueError(f"a = {a} не подходит: a^q mod p != 1.")

                # Ввод секретного ключа x
                x = input_int("Введите секретный ключ x (0 < x < q): ")

                # Установка параметров
                gost.set_params(p, q, a, x)

            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '2':
            if not gost.params_ready:
                print("Сначала установите параметры (пункт 1).")
            else:
                msg = input("Введите сообщение для подписи: ")
                try:
                    gost.sign(msg)
                except Exception as e:
                    print(f"Ошибка: {e}")

        elif choice == '3':
            if not gost.params_ready:
                print("Сначала установите параметры (пункт 1).")
            elif gost.last_signature == (None, None):
                print("Сначала подпишите сообщение (пункт 2).")
            else:
                try:
                    gost.verify()
                except Exception as e:
                    print(f"Ошибка: {e}")

        elif choice == '4':
            print("Программа завершена.")
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()
