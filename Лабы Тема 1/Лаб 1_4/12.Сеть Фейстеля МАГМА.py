# -*- coding: utf-8 -*-
"""
12. Перестановка в комбинационных шифрах (DES, ГОСТ 28147-89, МАГМА) — сеть Фейстеля.

Реализован блочный шифр «Магма» (ГОСТ Р 34.12-2015, 64 бита блок, 256 бит ключ, 32 раунда):
раундовая функция G[k], финальное преобразование G^*[k], расписание ключей — по RFC 8891.

Открытый текст: UTF-8, в начале 4 байта длины (big-endian), дополнение нулями до кратности 8 байт;
каждый 64-битный блок шифруется независимо (режим ECB для учебной демонстрации).
"""

import struct

# --- Фраза варианта (пустой ввод при запуске — подставляется она) ---
DEFAULT_PHRASE = "Леопард не может изменить своих пятен"

# Тестовый ключ 256 бит (64 hex-символа), приложение A.3 RFC 8891
DEFAULT_KEY_HEX = (
    "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
)

# Pi'_i — таблицы S-блоков (RFC 8891, раздел 4.1)
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
    a &= 0xFFFFFFFF
    out = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        out |= S_BOX[i][nibble] << (4 * i)
    return out & 0xFFFFFFFF


def t_inverse(b):
    b &= 0xFFFFFFFF
    out = 0
    for i in range(8):
        nibble = (b >> (4 * i)) & 0xF
        out |= S_BOX_INV[i][nibble] << (4 * i)
    return out & 0xFFFFFFFF


def rotl32(x, n):
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def g_round(k, a):
    """g[k](a) = (t(a + k mod 2^32)) <<< 11"""
    x = (a + k) & 0xFFFFFFFF
    x = t_direct(x)
    return rotl32(x, 11)


def G_feistel(k, a1, a0):
    """G[k](a1, a0) = (a0, g[k](a0) xor a1)"""
    return a0 & 0xFFFFFFFF, (g_round(k, a0) ^ a1) & 0xFFFFFFFF


def inv_G_feistel(k, new_a1, new_a0):
    """Обратное к G[k]."""
    old_a0 = new_a1
    old_a1 = (g_round(k, new_a1) ^ new_a0) & 0xFFFFFFFF
    return old_a1, old_a0


def round_keys_from_key(key32: bytes):
    """32 раундовых ключа K_1..K_32 (RFC 8891, раздел 4.3)."""
    if len(key32) != 32:
        raise ValueError("Ключ должен быть 32 байта (256 бит)")
    K = [int.from_bytes(key32[4 * i : 4 * (i + 1)], "big") for i in range(8)]
    rk = []
    for i in range(32):
        if i < 24:
            rk.append(K[i % 8])
        else:
            rk.append(K[7 - (i - 24)])
    return rk


def encrypt_block_magma(a1: int, a0: int, rk) -> tuple:
    """Один 64-битный блок: (старшая половина, младшая) — 32+32 бита."""
    for i in range(31):
        a1, a0 = G_feistel(rk[i], a1, a0)
    k = rk[31]
    out1 = (g_round(k, a0) ^ a1) & 0xFFFFFFFF
    out0 = a0 & 0xFFFFFFFF
    return out1, out0


def decrypt_block_magma(c1: int, c0: int, rk) -> tuple:
    """Расшифрование одного блока."""
    a0 = c0
    a1 = (g_round(rk[31], c0) ^ c1) & 0xFFFFFFFF
    for i in range(30, -1, -1):
        a1, a0 = inv_G_feistel(rk[i], a1, a0)
    return a1, a0


def pack64(a1: int, a0: int) -> bytes:
    return a1.to_bytes(4, "big") + a0.to_bytes(4, "big")


def unpack64(block8: bytes) -> tuple:
    if len(block8) != 8:
        raise ValueError("Блок должен быть 8 байт")
    a1 = int.from_bytes(block8[0:4], "big")
    a0 = int.from_bytes(block8[4:8], "big")
    return a1, a0


def feistel_encrypt_phrase(plaintext: str, key32: bytes) -> bytes:
    raw = plaintext.encode("utf-8")
    n = len(raw)
    body = struct.pack(">I", n) + raw
    pad = (8 - len(body) % 8) % 8
    body = body + bytes(pad)
    rk = round_keys_from_key(key32)
    out = bytearray()
    for i in range(0, len(body), 8):
        a1, a0 = unpack64(body[i : i + 8])
        c1, c0 = encrypt_block_magma(a1, a0, rk)
        out.extend(pack64(c1, c0))
    return bytes(out)


def feistel_decrypt_phrase(blob: bytes, key32: bytes) -> str:
    if len(blob) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8 байтам")
    rk = round_keys_from_key(key32)
    plain = bytearray()
    for i in range(0, len(blob), 8):
        c1, c0 = unpack64(blob[i : i + 8])
        a1, a0 = decrypt_block_magma(c1, c0, rk)
        plain.extend(pack64(a1, a0))
    n = struct.unpack(">I", plain[:4])[0]
    return plain[4 : 4 + n].decode("utf-8")


def parse_key_hex(hex_str: str) -> bytes:
    s = hex_str.strip().replace(" ", "")
    if len(s) != 64:
        raise ValueError("Ключ: ровно 64 шестнадцатеричных символа (256 бит)")
    return bytes.fromhex(s)


def _print_demo(phrase: str, key32: bytes):
    rk = round_keys_from_key(key32)
    print("=" * 60)
    print("Сеть Фейстеля — шифр «Магма» (ГОСТ Р 34.12-2015)")
    print("=" * 60)
    print(f"Исходный текст: {phrase}")
    print(f"Ключ (hex): {key32.hex()}")
    print(f"Число раундов: 32 (фиксировано стандартом МАГМА)")
    print("-" * 60)
    enc = feistel_encrypt_phrase(phrase, key32)
    print(f"Шифртекст (hex): {enc.hex()}")
    dec = feistel_decrypt_phrase(enc, key32)
    print(f"Расшифровано: {dec}")
    print(f"Совпадение с исходным: {'да' if dec == phrase else 'нет'}")
    print("=" * 60)


if __name__ == "__main__":
    print("Ввод фразы (Enter — вариант задания): ", end="")
    try:
        phrase_in = input().strip().lstrip("\ufeff")
    except EOFError:
        phrase_in = ""
    phrase = phrase_in if phrase_in else DEFAULT_PHRASE

    print("Ключ 256 бит, 64 hex-символа (Enter — тестовый ключ RFC 8891): ", end="")
    try:
        key_in = input().strip()
    except EOFError:
        key_in = ""
    try:
        key32 = parse_key_hex(key_in) if key_in else parse_key_hex(DEFAULT_KEY_HEX)
    except ValueError as e:
        print(f"Ошибка ключа: {e}")
        key32 = parse_key_hex(DEFAULT_KEY_HEX)
        print("Использован ключ по умолчанию.")

    _print_demo(phrase, key32)
