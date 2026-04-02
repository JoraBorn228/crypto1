"""
ШИФР АТБАШ
Русский алфавит (33 буквы с Ъ)
Первая буква алфавита заменяется последней, вторая — предпоследней и т.д.
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = len(ALPHABET)

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
            L = (N - 1 - m) % N
            result.append(num_to_char[L])
        else:
            result.append(char)
    return ''.join(result)


def decrypt(ciphertext):
    return encrypt(ciphertext)


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("ШИФР АТБАШ")
print("=" * 60)
print(f"Исходный текст: {original}")
encrypted = encrypt(original)
print(f"Зашифровано: {encrypted}")
print("-" * 60)
decrypted = decrypt(encrypted)
print(f"Расшифровано: {decrypted}")
print("-" * 60)
print(f"Совпадение: {original == decrypted}")
print("=" * 60)
