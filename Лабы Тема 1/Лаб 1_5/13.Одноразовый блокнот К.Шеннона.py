import sys

class ShannonCipher:
    def __init__(self):
        self.a = 1664525
        self.c = 1013904223
        self.m = 256
        self.state = 12345
        self.alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        self.last_gamma = []

    def get_char_index(self, ch):
        try:
            return self.alphabet.index(ch)
        except ValueError:
            return -1

    def is_russian_char(self, ch):
        return ch.upper() in self.alphabet or ch.upper() == 'Ё'

    def prepare_text(self, text):
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
                upper_ch = ch.upper()
                if upper_ch == 'Ё':
                    upper_ch = 'Е'
                if upper_ch in self.alphabet:
                    result.append(upper_ch)
        return ''.join(result)

    def restore_text(self, text):
        result = []
        i = 0
        length = len(text)
        while i < length:
            if i + 2 < length:
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

    def lcg(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def set_default_parameters(self):
        self.a = 1664525
        self.c = 1013904223
        self.m = 256
        self.state = 12345
        print("Установлены параметры по умолчанию:")
        print(f"a = {self.a}, c = {self.c}, m = {self.m}, seed = {self.state}")

    def set_parameters(self, a, c, m, seed):
        valid = True
        errors = []

        if a <= 1:
            valid = False
            errors.append("- a должно быть больше 1")
        if a % 4 != 1:
            valid = False
            errors.append("- a mod 4 должно быть равно 1")
        if c % 2 == 0:
            valid = False
            errors.append("- c должно быть нечетным")
        if (m & (m - 1)) != 0:
            valid = False
            errors.append("- m должно быть степенью двойки")

        if not valid:
            print("\nОШИБКА: Параметры не соответствуют требованиям:")
            for err in errors:
                print(err)
            return False

        self.a = a
        self.c = c
        self.m = m
        self.state = seed
        print("\nПараметры приняты и обеспечивают максимальный период")
        print(f"a = {self.a}, c = {self.c}, m = {self.m}, T(0) = {self.state}")
        return True

    def encrypt(self, text):
        prepared = self.prepare_text(text)
        if not prepared:
            print("Ошибка: текст пуст!")
            return

        self.last_gamma.clear()
        numbers = []
        letters = []

        for ch in prepared:
            idx = self.get_char_index(ch)
            if idx == -1:
                print(f"Ошибка: символ {ch} не найден в алфавите!")
                return

            gamma = self.lcg() % 32
            self.last_gamma.append(gamma)

            enc_idx = (idx + gamma) % 32
            enc_ch = self.alphabet[enc_idx]

            numbers.append(enc_idx)
            letters.append(enc_ch)

        raw_cipher = ''.join(letters)

        # Группировка по 5 символов
        grouped = ' '.join(raw_cipher[i:i+5] for i in range(0, len(raw_cipher), 5))

        print("\nЗашифрованный текст: ")
        print("В виде цифр:", ' '.join(str(x) for x in numbers))
        print(f"В виде букв: {grouped}")

    def decrypt(self, encrypted_text, gamma):
        cleaned_text = ''.join(encrypted_text.split())

        if len(cleaned_text) != len(gamma):
            print(f"Ошибка: длина текста ({len(cleaned_text)}) не совпадает с длиной гаммы ({len(gamma)})!")
            return

        temp_chars = []
        for i, ch in enumerate(cleaned_text):
            idx = self.get_char_index(ch)
            if idx == -1:
                print(f"Ошибка: символ {ch} не найден в алфавите!")
                return
            dec_idx = (idx - gamma[i] + 32) % 32
            temp_chars.append(self.alphabet[dec_idx])

        temp = ''.join(temp_chars)
        result = self.restore_text(temp)
        print("\nРасшифрованный текст:")
        print(result)

    def get_last_gamma(self):
        return self.last_gamma

    def print_alphabet(self):
        print("\nАлфавит (32 буквы, индексы 0-31):")
        for i, ch in enumerate(self.alphabet):
            print(f"{i}:{ch}", end=' ')
            if (i + 1) % 8 == 0:
                print()
        print()


def process_user_input(cipher):
    print("\n1. Задать параметры генератора")
    print("2. Зашифровать текст")
    print("3. Расшифровать текст")
    print("4. Выход")
    choice = input("Ваш выбор: ").strip()

    if choice == '1':
        try:
            m = int(input("Введите модуль m (степень двойки): "))
            a = int(input("Введите множитель a (a > 1, a mod 4 = 1): "))
            c = int(input("Введите приращение c (нечетное): "))
            seed = int(input("Введите начальное значение T(0): "))
            cipher.set_parameters(a, c, m, seed)
        except ValueError:
            print("Ошибка: введите целые числа.")

    elif choice == '2':
        text = input("Введите текст для шифрования: ")
        cipher.encrypt(text)

    elif choice == '3':
        encrypted = input("Введите зашифрованный текст: ")
        gamma = cipher.get_last_gamma()
        if not gamma:
            print("Ошибка: сначала нужно зашифровать текст!")
        else:
            cipher.decrypt(encrypted, gamma)

    elif choice == '4':
        print("Программа завершена.")
        sys.exit(0)

    else:
        print("Неверный выбор!")


def main():
    print("Одноразовый блокнот Шеннона")
    cipher = ShannonCipher()
    while True:
        process_user_input(cipher)


if __name__ == "__main__":
    main()
