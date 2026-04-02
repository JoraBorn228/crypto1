"""
ПРОСТОЙ ШИФР ТРИТЕМИЯ
Русский алфавит (33 буквы с Ъ)
"""

# Алфавит
ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = 33  # длина алфавита

# Словари для перевода букв в числа и обратно
char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}


def encrypt(text):
    text = text.upper()
    result = []
    pos = 0  # счётчик позиции ТОЛЬКО для букв

    for char in text:
        if char == ' ':
            # пробел остаётся пробелом
            result.append(' ')
        elif char in char_to_num:
            m = char_to_num[char]  # номер исходной буквы
            k = 2 * pos + 1  # смещение зависит от номера буквы
            L = (m + k) % N  # номер зашифрованной буквы
            result.append(num_to_char[L])
            pos += 1  # увеличиваем счётчик ТОЛЬКО для букв
        else:
            # другие символы (знаки препинания) оставляем как есть
            result.append(char)
            # для знаков препинания счётчик НЕ увеличиваем

    return ''.join(result)


def decrypt(ciphertext):
    ciphertext = ciphertext.upper()
    result = []
    pos = 0  # счётчик позиции ТОЛЬКО для букв

    for char in ciphertext:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            L = char_to_num[char]  # номер зашифрованной буквы
            k = 2 * pos + 1  # смещение
            m = (L - k) % N  # номер исходной буквы
            result.append(num_to_char[m])
            pos += 1  # увеличиваем счётчик ТОЛЬКО для букв
        else:
            result.append(char)

    return ''.join(result)


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("ПРОСТОЙ ШИФР ТРИТЕМИЯ")
print("=" * 60)
print(f"Исходный текст: {original}")
encrypted = encrypt(original)
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
