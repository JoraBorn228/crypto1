"""
ШИФР ЦЕЗАРЯ
Русский алфавит (33 буквы с Ъ)
Сдвиг на K позиций по кольцу алфавита (K можно изменить под вариант задания).
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = len(ALPHABET)

# Сдвиг шифра Цезаря (подставьте значение из варианта задания при необходимости)
K = 7

char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}


def encrypt(text):
    text = text.upper()
    result = []
    for char in text:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            m = char_to_num[char]
            L = (m + K) % N
            result.append(num_to_char[L])
        else:
            result.append(char)
    return ''.join(result)


def decrypt(ciphertext):
    ciphertext = ciphertext.upper()
    result = []
    for char in ciphertext:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            L = char_to_num[char]
            m = (L - K) % N
            result.append(num_to_char[m])
        else:
            result.append(char)
    return ''.join(result)


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("ШИФР ЦЕЗАРЯ")
print("=" * 60)
print(f"Сдвиг K = {K}")
print(f"Исходный текст: {original}")
encrypted = encrypt(original)
print(f"Зашифровано: {encrypted}")
print("-" * 60)
decrypted = decrypt(encrypted)
print(f"Расшифровано: {decrypted}")
print("-" * 60)
print(f"Совпадение: {original == decrypted}")
print("=" * 60)
