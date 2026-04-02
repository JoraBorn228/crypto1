"""
КВАДРАТ ПОЛИБИЯ (русский алфавит)
Сетка 6×6: буквы алфавита (33 шт.) заполняют ячейки по строкам;
каждая буква кодируется парой координат (номер строки, номер столбца), 1…6.
Шифртекст: пары цифр, пары разделяются пробелом. Пробелы в тексте сохраняются.
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ROWS, COLS = 6, 6


def _build_maps():
    char_to_rc = {}
    index_to_char = {}
    for idx, char in enumerate(ALPHABET):
        r, c = idx // COLS, idx % COLS
        char_to_rc[char] = (r + 1, c + 1)
        index_to_char[idx] = char
    return char_to_rc, index_to_char


char_to_rc, index_to_char = _build_maps()


def encrypt(text):
    text = text.upper()
    parts = []
    for char in text:
        if char == ' ':
            parts.append(' ')
        elif char in char_to_rc:
            r, c = char_to_rc[char]
            parts.append(f"{r}{c}")
        else:
            parts.append(char)
    return ' '.join(p for p in parts if p != '') if False else _join_polybius(parts)


def _join_polybius(parts):
    out = []
    for i, p in enumerate(parts):
        if p == ' ':
            out.append(' ')
        elif len(p) == 2 and p.isdigit():
            out.append(p)
        else:
            out.append(p)
    return ''.join(
        ((' ' if (out[i - 1] not in (' ',) and out[i] != ' ' and out[i - 1][-1].isdigit() and out[i][0].isdigit()) else '') + out[i])
        if i > 0 else out[i]
        for i in range(len(out))
    )


def encrypt(text):
    text = text.upper()
    chunks = []
    for char in text:
        if char == ' ':
            chunks.append(' ')
        elif char in char_to_rc:
            r, c = char_to_rc[char]
            chunks.append(f"{r}{c}")
        else:
            chunks.append(char)
    result = []
    for i, ch in enumerate(chunks):
        if ch == ' ':
            result.append(' ')
        elif len(ch) == 2 and ch.isdigit():
            if result and result[-1] not in (' ',) and result[-1][-1].isdigit():
                result.append(' ')
            result.append(ch)
        else:
            result.append(ch)
    return ''.join(result)


def decrypt(ciphertext):
    s = ciphertext.upper().strip()
    result = []
    i = 0
    while i < len(s):
        if s[i] == ' ':
            result.append(' ')
            i += 1
            continue
        if i + 1 < len(s) and s[i].isdigit() and s[i + 1].isdigit():
            r, c = int(s[i]) - 1, int(s[i + 1]) - 1
            if 0 <= r < ROWS and 0 <= c < COLS:
                idx = r * COLS + c
                if idx < len(ALPHABET):
                    result.append(index_to_char[idx])
                else:
                    result.append('?')
            i += 2
            continue
        result.append(s[i])
        i += 1
    return ''.join(result)


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("КВАДРАТ ПОЛИБИЯ")
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
