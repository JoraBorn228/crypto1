import sys
import math

# ---- Вспомогательные математические функции ----
def mod_pow(a, exp, mod):
    """Быстрое возведение в степень по модулю"""
    result = 1
    a %= mod
    while exp > 0:
        if exp & 1:
            result = (result * a) % mod
        a = (a * a) % mod
        exp >>= 1
    return result

def mod_inverse(a, m):
    """Расширенный алгоритм Евклида для нахождения обратного элемента"""
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def is_prime(n):
    """Проверка простоты (для небольших чисел)"""
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

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


class RSACipher:
    def __init__(self):
        self.p = self.q = self.N = self.phi = self.E = self.D = 0
        self.key_set = False
        self.alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"   # 32 буквы

    def to_upper_russian(self, c):
        """Приведение русской буквы к верхнему регистру, Ё -> Е"""
        if 'а' <= c <= 'я' or 'А' <= c <= 'Я':
            return c.upper()
        if c == 'ё' or c == 'Ё':
            return 'Е'
        return c

    def is_russian_char(self, c):
        """Проверка, является ли символ русской буквой (включая Ё)"""
        return ('А' <= c <= 'Я') or ('а' <= c <= 'я') or c in ('Ё', 'ё')

    def prepare_text(self, text):
        """Подготовка текста: пробел -> ПРБ, точка -> ТЧК, запятая -> ЗПТ, кавычка -> КВЧ"""
        result = []
        for ch in text:
            if ch == ' ':
                result.append("ПРБ")
            elif ch == '.':
                result.append("ТЧК")
            elif ch == ',':
                result.append("ЗПТ")
            elif ch == '"':
                result.append("КВЧ")
            else:
                upper = self.to_upper_russian(ch)
                if self.is_russian_char(upper):
                    result.append(upper)
        return ''.join(result)

    def restore_text(self, text):
        """Восстановление пробелов, точек, запятых и кавычек после расшифровки"""
        result = []
        i = 0
        n = len(text)
        while i < n:
            if i + 2 < n:
                triple = text[i:i+3]
                if triple == "ПРБ":
                    result.append(' ')
                    i += 3
                    continue
                elif triple == "ТЧК":
                    result.append('.')
                    i += 3
                    continue
                elif triple == "ЗПТ":
                    result.append(',')
                    i += 3
                    continue
                elif triple == "КВЧ":
                    result.append('"')
                    i += 3
                    continue
            result.append(text[i])
            i += 1
        return ''.join(result)

    def char_to_int(self, c):
        """Буква -> число 1..32 (нумерация с 1)"""
        try:
            return self.alphabet.index(c) + 1
        except ValueError:
            return -1

    def int_to_char(self, n):
        """Число 1..32 -> буква"""
        if 1 <= n <= len(self.alphabet):
            return self.alphabet[n-1]
        return '?'

    # ---- Установка ключа ----
    def set_key(self, prime_p, prime_q, exp_e):
        if not is_prime(prime_p):
            raise ValueError("p не является простым числом.")
        if not is_prime(prime_q):
            raise ValueError("q не является простым числом.")
        if prime_p == prime_q:
            raise ValueError("p и q должны быть разными.")

        N = prime_p * prime_q
        phi = (prime_p - 1) * (prime_q - 1)

        if exp_e <= 1 or exp_e >= phi:
            raise ValueError("E должно быть в диапазоне 1 < E < ф(N).")

        if gcd(exp_e, phi) != 1:
            raise ValueError("E и ф(N) должны быть взаимно просты.")

        if N < 32:
            raise ValueError(f"Модуль N = {N} слишком мал для кодирования алфавита.")

        private_exponent = mod_inverse(exp_e, phi)

        if exp_e == private_exponent:
            raise ValueError("Открытый и секретный показатели совпадают; выберите другое E.")

        self.p = prime_p
        self.q = prime_q
        self.N = N
        self.phi = phi
        self.E = exp_e
        self.D = private_exponent

        self.key_set = True

        print("\nКЛЮЧИ УСТАНОВЛЕНЫ")
        print(f"p = {self.p}, q = {self.q}")
        print(f"N = {self.N}")
        print(f"ф(N) = {self.phi}")
        print(f"Открытый ключ (E, N) = ({self.E}, {self.N})")
        print(f"Секретный ключ D = {self.D}")
        return True

    # ---- Шифрование ----
    def encrypt(self, plain_text):
        if not self.key_set:
            print("Ошибка: ключ не установлен!")
            return ""

        prepared = self.prepare_text(plain_text)
        if not prepared:
            print("Ошибка: текст пуст!")
            return ""

        print(f"\nТекст после обработки: {prepared}")

        cipher_nums = []
        print("\n--- ШИФРОВАНИЕ ---")
        print("Символ -> Код -> Шифр")
        print("-------------------------------")

        for ch in prepared:
            m = self.char_to_int(ch)
            if m == -1:
                print(f"Ошибка: символ {ch} не найден в алфавите!")
                return ""
            ciph = mod_pow(m, self.E, self.N)
            cipher_nums.append(ciph)
            print(f"   {ch}    ->    {m:2d}     -> {ciph}")

        # Формируем строку с числами через пробел
        result = ' '.join(str(x) for x in cipher_nums)

        print("\nЗАШИФРОВАННЫЙ ТЕКСТ")
        print(result)
        return result

    # ---- Расшифровка ----
    def decrypt(self, cipher_text):
        if not self.key_set:
            print("Ошибка: ключ не установлен!")
            return ""

        # Разбираем строку с числами, разделёнными пробелами
        parts = cipher_text.strip().split()
        if not parts:
            print("Ошибка: не удалось разобрать зашифрованный текст!")
            return ""
        try:
            cipher_nums = [int(x) for x in parts]
        except ValueError:
            print("Ошибка: зашифрованный текст должен содержать только целые числа!")
            return ""

        print("\n--- РАСШИФРОВАНИЕ ---")
        print("Шифр -> Код -> Символ")
        print("-------------------------------")

        decrypted_chars = []
        for ciph in cipher_nums:
            m = mod_pow(ciph, self.D, self.N)
            if m < 1 or m > len(self.alphabet):
                print(f"Ошибка: расшифрованное число {m} вне диапазона 1..32!")
                return ""
            ch = self.int_to_char(m)
            decrypted_chars.append(ch)
            print(f"{ciph} ->    {m:2d}     -> {ch}")

        decrypted_str = ''.join(decrypted_chars)
        result = self.restore_text(decrypted_str)
        print("\nРАСШИФРОВАННЫЙ ТЕКСТ")
        print(result)
        return result


def process_user_input(cipher):
    print("\nRSA")
    print("1. Установить ключ (p, q, e)")
    print("2. Зашифровать текст")
    print("3. Расшифровать текст")
    print("4. Выход")
    choice = input("Ваш выбор: ").strip()

    if choice == '1':
        try:
            p = int(input("Введите простое число p (например, 23): "))
            q = int(input("Введите простое число q (например, 29): "))
            e = int(input("Введите открытый ключ e (например, 3 или 65537): "))
            cipher.set_key(p, q, e)
        except ValueError:
            print("Ошибка: введите целые числа.")
    elif choice == '2':
        text = input("Введите текст для шифрования: ")
        cipher.encrypt(text)
    elif choice == '3':
        text = input("Введите зашифрованный текст (числа через пробел): ")
        cipher.decrypt(text)
    elif choice == '4':
        print("Программа завершена.")
        sys.exit(0)
    else:
        print("Неверный выбор!")


def main():
    cipher = RSACipher()
    while True:
        process_user_input(cipher)


if __name__ == "__main__":
    main()

