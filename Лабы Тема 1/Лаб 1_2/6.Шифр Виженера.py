# -*- coding: utf-8 -*-
"""
ПРОСТОЙ ШИФР ВИЖЕНЕРА
Русский алфавит (33 буквы с Ъ)
Ключевое слово: КЛЮЧ
Пробелы сохраняются
"""

# Алфавит
ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = 33  # длина алфавита

# Словари для перевода
char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}

# Ключ (можно изменить на любой)
KEYWORD = "ШИФР"


def get_key_nums(keyword):
    """Переводит ключевое слово в числа"""
    return [char_to_num[char] for char in keyword.upper() if char in char_to_num]


def encrypt(text, keyword=KEYWORD):
    text = text.upper()
    key_nums = get_key_nums(keyword)
    key_length = len(key_nums)

    result = []
    key_idx = 0  # индекс в ключе

    for char in text:
        if char == ' ':
            result.append(' ')  # пробел остаётся
        elif char in char_to_num:
            vi = char_to_num[char]  # номер исходной буквы
            ki = key_nums[key_idx % key_length]  # буква ключа
            wi = (vi + ki) % N  # номер зашифрованной
            result.append(num_to_char[wi])
            key_idx += 1  # ключ двигаем только на буквах
        else:
            result.append(char)  # другие символы

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
            wi = char_to_num[char]  # номер зашифрованной
            ki = key_nums[key_idx % key_length]  # буква ключа
            vi = (wi - ki) % N  # номер исходной
            result.append(num_to_char[vi])
            key_idx += 1
        else:
            result.append(char)

    return ''.join(result)


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("ПРОСТОЙ ШИФР")
print("=" * 60)
encrypted = encrypt(original)

print(f"Исходный текст: {original}")
print(f"Зашифровано: {encrypted}")

print("-" * 60)

# Шифрование
encrypted = encrypt(original)
print(f"Зашифровано: {encrypted}")

# Расшифровка
decrypted = decrypt(encrypted)
print(f"Расшифровано: {decrypted}")

# Проверка
print("-" * 60)
print(f"Совпадение: {original == decrypted}")
print("=" * 60)
