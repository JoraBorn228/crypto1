# -*- coding: utf-8 -*-
"""
ПРОСТОЙ ШИФР БЕЛАЗО
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = 33

char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}

KEYWORD = "КЛЮЧ"


def get_key_nums(keyword):
    return [char_to_num[char] for char in keyword.upper() if char in char_to_num]


def encrypt(text, keyword=KEYWORD):
    text = text.upper()
    key_nums = get_key_nums(keyword)
    key_length = len(key_nums)

    result = []
    key_idx = 0

    for char in text:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            vi = char_to_num[char]
            ki = key_nums[key_idx % key_length]
            wi = (vi + ki) % N
            result.append(num_to_char[wi])
            key_idx += 1
        else:
            result.append(char)

    return ''.join(result)


def decrypt(ciphertext, keyword=KEYWORD):
    ciphertext = ciphertext.upper()
    key_nums = get_key_nums(keyword)
    key_length = len(key_nums)

    result = []
    key_idx = 0

    for char in ciphertext:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            wi = char_to_num[char]
            ki = key_nums[key_idx % key_length]
            vi = (wi - ki) % N
            result.append(num_to_char[vi])
            key_idx += 1
        else:
            result.append(char)

    return ''.join(result)


while True:
    print("\n" + "=" * 50)
    print("ПРОСТОЙ ШИФР БЕЛАЗО")
    print("=" * 50)
    print("1. Зашифровать")
    print("2. Расшифровать")
    print("3. Выход")

    choice = input("\nВыберите действие: ")

    if choice == "1":
        text = input("Введите текст для шифрования: ")
        key = input("Введите ключ (Enter = КЛЮЧ): ").strip()

        if not key:
            key = KEYWORD

        encrypted = encrypt(text, key)

        print("\nРезультат шифрования:")
        print(encrypted)

    elif choice == "2":
        text = input("Введите текст для расшифрования: ")
        key = input("Введите ключ (Enter = КЛЮЧ): ").strip()

        if not key:
            key = KEYWORD

        decrypted = decrypt(text, key)

        print("\nРезультат расшифрования:")
        print(decrypted)

    elif choice == "3":
        print("Выход из программы...")
        break

    else:
        print("Неверный выбор!")