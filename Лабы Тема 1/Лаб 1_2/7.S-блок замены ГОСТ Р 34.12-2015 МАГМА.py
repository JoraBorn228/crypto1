# -*- coding: utf-8 -*-
"""
S-блок замены (нелинейное преобразование t) блочного шифра «Магма»
по ГОСТ Р 34.12-2015.

32-битное слово представляется как восемь 4-битных частей
a = a_7||...||a_0 (нумерация от младших разрядов к старшим):
a_0 — младший полубайт, a_7 — старший.

t(a) = Pi_7(a_7)||...||Pi_0(a_0), где Pi_i — таблица замены (подстановка Pi'_i).

Таблицы Pi'_0 … Pi'_7 — из RFC 8891 / раздел 4.1 ГОСТ Р 34.12-2015.
Тестовые векторы для t — приложение A.1 RFC 8891.

Демонстрация на фразе: текст кодируется в UTF-8, к началу добавляется 4 байта
длины (big-endian), блок дополняется нулями до кратности 4 байтам; каждое
32-битное слово (байты старший→младший, как в ГОСТ) прогоняется через t.
"""

import struct

# Фраза варианта задания — шифруется в блоке if __name__ == "__main__"
PHRASE = "Леопард не может изменить своих пятен"

# Pi'_i(j) — значение в ячейке j (вход 0..15), i = 0..7
S_BOX = (
    (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
    (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
    (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
    (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
    (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
    (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
    (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
    (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2),
)


def _build_inverse_boxes():
    inv = []
    for box in S_BOX:
        rev = [0] * 16
        for x in range(16):
            rev[box[x]] = x
        inv.append(tuple(rev))
    return tuple(inv)


S_BOX_INV = _build_inverse_boxes()


def t_direct(a):
    """Прямое S-преобразование t над 32-битным словом (беззнаковое)."""
    a &= 0xFFFFFFFF
    out = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        out |= S_BOX[i][nibble] << (4 * i)
    return out & 0xFFFFFFFF


def t_inverse(b):
    """Обратное S-преобразование (обратная подстановка по каждому полубайту)."""
    b &= 0xFFFFFFFF
    out = 0
    for i in range(8):
        nibble = (b >> (4 * i)) & 0xF
        out |= S_BOX_INV[i][nibble] << (4 * i)
    return out & 0xFFFFFFFF


def _bytes_to_words_be(data):
    """Четыре байта подряд -> 32-битное слово (big-endian)."""
    words = []
    for i in range(0, len(data), 4):
        w = data[i] << 24 | data[i + 1] << 16 | data[i + 2] << 8 | data[i + 3]
        words.append(w)
    return words


def _words_to_bytes_be(words):
    out = bytearray()
    for w in words:
        out.extend(
            (
                (w >> 24) & 0xFF,
                (w >> 16) & 0xFF,
                (w >> 8) & 0xFF,
                w & 0xFF,
            )
        )
    return bytes(out)


def phrase_encrypt(plaintext):
    """
    Применяет t к каждому 32-битному слову представления фразы.
    Возвращает байтовый результат (для вывода удобно смотреть hex).
    """
    raw = plaintext.encode("utf-8")
    n = len(raw)
    body = struct.pack(">I", n) + raw
    pad = (4 - len(body) % 4) % 4
    body = body + bytes(pad)
    words = _bytes_to_words_be(body)
    enc_words = [t_direct(w) for w in words]
    return _words_to_bytes_be(enc_words)


def phrase_decrypt(blob):
    """Обратное: t^-1 по словам и восстановление UTF-8 строки."""
    words = _bytes_to_words_be(blob)
    dec_words = [t_inverse(w) for w in words]
    body = _words_to_bytes_be(dec_words)
    n = struct.unpack(">I", body[:4])[0]
    return body[4 : 4 + n].decode("utf-8")


if __name__ == "__main__":
    # Приложение A.1 RFC 8891 (цепочка преобразований t)
    tests = (
        (0xFDB97531, 0x2A196F34),
        (0x2A196F34, 0xEBD9F03A),
        (0xEBD9F03A, 0xB039BB3D),
        (0xB039BB3D, 0x68695433),
    )

    print("=" * 60)
    print("S-блок замены «Магма» (ГОСТ Р 34.12-2015), преобразование t")
    print("=" * 60)

    for x, expected in tests:
        y = t_direct(x)
        ok = "да" if y == expected else "НЕТ"
        print(f"t({x:08X}) = {y:08X}  (ожид. {expected:08X})  OK: {ok}")

    print("-" * 60)
    x0 = 0xFDB97531
    r = t_direct(x0)
    back = t_inverse(r)
    print(f"Проверка обратимости: t^(-1)(t({x0:08X})) = {back:08X}")
    print(f"Совпадение с исходным: {'да' if back == x0 else 'нет'}")
    print("=" * 60)

    print()
    print("=" * 60)
    print("Шифрование фразы варианта (S-слой t по 32-битным словам)")
    print("=" * 60)
    phrase = PHRASE
    print(f"Исходный текст: {phrase}")

    enc_bytes = phrase_encrypt(phrase)
    print(f"После t (hex): {enc_bytes.hex()}")
    dec = phrase_decrypt(enc_bytes)
    print(f"После t^(-1): {dec}")
    print(f"Совпадение с исходной фразой: {'да' if dec == phrase else 'нет'}")
    print("=" * 60)
