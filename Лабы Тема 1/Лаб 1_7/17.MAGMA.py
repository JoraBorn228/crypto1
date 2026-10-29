# -*- coding: utf-8 -*-
"""
17. Шифр МАГМА (ГОСТ Р 34.12-2015)

Реализация блочного шифра «Магма» с режимом ECB.
Блок: 64 бита, ключ: 256 бит, 32 раунда (сеть Фейстеля).
Тестирование по ГОСТ Р 34.12-2018 (Приложение А).

Источник: ЛАБКРИПТ_2022, Блок G, задание 17.

ВВОД (как в методичке):

  - Открытый текст: произвольная строка (кодируется в UTF-8)
  - Ключ: 64 шестнадцатеричных символа (256 бит)

АЛГОРИТМ (по ГОСТ Р 34.12-2018 раздел 5):
  Блок a = a1|a0 (a1 — старшие 32 бит, a0 — младшие 32 бит).
  Раунд: G[k](a1,a0) = (a0, g[k](a0) XOR a1)
  Последний раунд: G*[k](a1,a0) = (g[k](a0) XOR a1, a0)
  Ключ K делится на K1..K8 (big-endian, 32 бит каждый).
  Расписание: K1..K8 × 3, затем K8..K1.
"""

# ─────────────────────────────────────────────
#  S-блоки ГОСТ Р 34.12-2015 (Приложение А)
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
#  Нелинейное преобразование T (8 × S-блоков)
# ─────────────────────────────────────────────

def t_direct(a: int) -> int:
    a &= 0xFFFFFFFF
    out = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0xF
        out |= S_BOX[i][nibble] << (4 * i)
    return out & 0xFFFFFFFF


# ─────────────────────────────────────────────
#  Циклический сдвиг влево на 11 бит
# ─────────────────────────────────────────────

def rotl32(x: int, n: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


# ─────────────────────────────────────────────
#  Раундовая функция g[k](a) = rotl11(T(a + k mod 2^32))
# ─────────────────────────────────────────────

def g_round(k: int, a: int) -> int:
    x = (a + k) & 0xFFFFFFFF
    x = t_direct(x)
    return rotl32(x, 11)


# ─────────────────────────────────────────────
#  Расписание ключей
#  K = K1|K2|...|K8 (big-endian 32-бит слова)
#  Раунды 1-24: K1,K2,...,K8 повторить 3 раза
#  Раунды 25-32: K8,K7,...,K1
# ─────────────────────────────────────────────

def round_keys_from_key(key32: bytes) -> list:
    if len(key32) != 32:
        raise ValueError("Ключ должен быть 32 байта (256 бит)")
    K = [int.from_bytes(key32[4 * i: 4 * (i + 1)], "big") for i in range(8)]
    rk = []
    for i in range(32):
        if i < 24:
            rk.append(K[i % 8])
        else:
            rk.append(K[7 - (i - 24)])
    return rk


# ─────────────────────────────────────────────
#  Шифрование одного 64-битного блока (big-endian)
#  a = a1|a0  (a1 — старшие 32 бит, a0 — младшие 32 бит)
#  G[k](a1,a0)  = (a0,  g[k](a0) XOR a1)   — обычный раунд
#  G*[k](a1,a0) = (g[k](a0) XOR a1, a0)    — последний раунд
# ─────────────────────────────────────────────

def encrypt_block_magma(block: bytes, rk: list) -> bytes:
    a1 = int.from_bytes(block[0:4], "big")
    a0 = int.from_bytes(block[4:8], "big")
    for i in range(31):
        # G[rk[i]](a1, a0)
        a1, a0 = a0, (g_round(rk[i], a0) ^ a1) & 0xFFFFFFFF
    # G*[rk[31]](a1, a0) — без перестановки полублоков
    b1 = (g_round(rk[31], a0) ^ a1) & 0xFFFFFFFF
    b0 = a0
    return b1.to_bytes(4, "big") + b0.to_bytes(4, "big")


def decrypt_block_magma(block: bytes, rk: list) -> bytes:
    b1 = int.from_bytes(block[0:4], "big")
    b0 = int.from_bytes(block[4:8], "big")
    # Обратное G*[rk[31]]: a1 = g[k](b0) XOR b1, a0 = b0
    a1 = (g_round(rk[31], b0) ^ b1) & 0xFFFFFFFF
    a0 = b0
    # Обратные раунды 30..0
    for i in range(30, -1, -1):
        # Обратное G[rk[i]](a1, a0) = (old_a0, ...) = (a0 прежде свопа)
        # G дало: new_a1=a0_old, new_a0 = g[k](a0_old) XOR a1_old
        # Значит: a0_old = a1, a1_old = g[k](a1) XOR a0
        a1, a0 = (g_round(rk[i], a1) ^ a0) & 0xFFFFFFFF, a1
    return a1.to_bytes(4, "big") + a0.to_bytes(4, "big")


# ─────────────────────────────────────────────
#  ECB-режим с PKCS#7-дополнением (блок 8 байт)
# ─────────────────────────────────────────────

def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    if not data:
        raise ValueError("Нельзя снять дополнение с пустых данных.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8 or data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Неверный ключ или повреждённый шифртекст: дополнение некорректно.")
    return data[:-pad_len]


def magma_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    padded = pad_pkcs7(plaintext, 8)
    ciphertext = b''
    for i in range(0, len(padded), 8):
        ciphertext += encrypt_block_magma(padded[i:i + 8], rk)
    return ciphertext


def magma_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    plaintext = b''
    for i in range(0, len(ciphertext), 8):
        plaintext += decrypt_block_magma(ciphertext[i:i + 8], rk)
    return unpad_pkcs7(plaintext)


# ─────────────────────────────────────────────
#  Тест по ГОСТ Р 34.12-2018 (Приложение А)
# ─────────────────────────────────────────────

def test_gost_vectors():
    print("=" * 70)
    print("ТЕСТ МАГМА по ГОСТ Р 34.12-2018 (Приложение А)")
    print("=" * 70)
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    plaintext          = bytes.fromhex("fedcba9876543210")
    expected_ciphertext= bytes.fromhex("4ee901e5c2d8ca3d")

    rk         = round_keys_from_key(key)
    ciphertext = encrypt_block_magma(plaintext, rk)
    decrypted  = decrypt_block_magma(ciphertext, rk)

    print(f"Ключ (hex)        : {key.hex()}")
    print(f"Открытый текст    : {plaintext.hex()}")
    print(f"Ожидаемый шифр    : {expected_ciphertext.hex()}")
    print(f"Полученный шифр   : {ciphertext.hex()}")
    print(f"Тест шифрования   : {'ДА ✓' if ciphertext == expected_ciphertext else 'НЕТ ✗'}")
    print(f"Расшифрование     : {decrypted.hex()}")
    print(f"Тест расшифрования: {'ДА ✓' if decrypted == plaintext else 'НЕТ ✗'}")
    print("=" * 70)
    return ciphertext == expected_ciphertext and decrypted == plaintext


# ─────────────────────────────────────────────
#  Ввод ключа от пользователя
# ─────────────────────────────────────────────

def read_key_from_user() -> bytes:
    """Запрашивает 256-битный ключ в виде 64 hex-символов."""
    print("Ключ вводится как 64 шестнадцатеричных символа (256 бит).")
    print("Пример: ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff")
    key_hex = input("Введите ключ: ").strip().replace(" ", "")
    if len(key_hex) != 64:
        raise ValueError("Ключ должен содержать ровно 64 hex-символа (32 байта).")
    try:
        return bytes.fromhex(key_hex)
    except ValueError as exc:
        raise ValueError("Ключ должен состоять только из символов 0-9 и A-F.") from exc


# ─────────────────────────────────────────────
#  Интерактивные функции
# ─────────────────────────────────────────────

def interactive_encrypt_hex():
    """
    Зашифровать hex-блок (как в контрольном примере ГОСТ Р 34.12-2018).
    Ввод : hex-строка, кратная 16 символам (= 8 байт на блок).
    Пример: PT = fedcba9876543210  →  CT = 4ee901e5c2d8ca3d
    """
    pt_hex = input("Введите открытый текст в hex (кратно 16 символам): ").strip().replace(" ", "")
    if not pt_hex:
        raise ValueError("Блок не должен быть пустым.")
    if len(pt_hex) % 16 != 0:
        raise ValueError("Длина hex должна быть кратна 16 (8 байт на блок).")
    try:
        pt_bytes = bytes.fromhex(pt_hex)
    except ValueError as exc:
        raise ValueError("Допустимы только символы 0-9 и A-F.") from exc
    key = read_key_from_user()
    rk = round_keys_from_key(key)
    ciphertext = b''
    for i in range(0, len(pt_bytes), 8):
        ciphertext += encrypt_block_magma(pt_bytes[i:i + 8], rk)
    print(f"Шифртекст (hex): {ciphertext.hex()}")





def interactive_decrypt():
    """Расшифровать hex-шифртекст."""
    ciphertext_hex = input("Введите шифртекст в hex: ").strip().replace(" ", "")
    if not ciphertext_hex:
        raise ValueError("Шифртекст не должен быть пустым.")
    if len(ciphertext_hex) % 16 != 0:
        raise ValueError("Длина hex-шифртекста должна быть кратна 16 символам (8 байт на блок).")
    try:
        ciphertext = bytes.fromhex(ciphertext_hex)
    except ValueError as exc:
        raise ValueError("Шифртекст должен состоять только из символов 0-9 и A-F.") from exc
    key = read_key_from_user()
    plaintext = magma_ecb_decrypt(ciphertext, key)
    try:
        print(f"Открытый текст: {plaintext.decode('utf-8')}")
    except UnicodeDecodeError:
        print(f"Результат (hex): {plaintext.hex()}")


# ─────────────────────────────────────────────
#  Главное меню
# ─────────────────────────────────────────────

def interactive_menu():
    print("\n" + "=" * 70)
    print("ШИФР МАГМА (ГОСТ Р 34.12-2015)  —  Задание 17")
    print("Сеть Фейстеля, 32 раунда, блок 64 бит, ключ 256 бит")
    print("Источник: ЛАБКРИПТ_2022, Блок G, стр. 29")
    print("=" * 70)
    print()
    print("ВВОД:")
    print("  Открытый текст : hex-строка, кратная 16 символам (8 байт на блок)")
    print("  Ключ           : 64 шестнадцатеричных символа (256 бит)")
    print("  Пример ГОСТ    : PT=fedcba9876543210 → CT=4ee901e5c2d8ca3d")
    print()

    while True:
        print("1 — Зашифровать hex-блок")
        print("2 — Расшифровать hex-шифртекст")
        print("0 — Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            try:
                interactive_encrypt_hex()
            except (ValueError, UnicodeError) as exc:
                print(f"Ошибка ввода: {exc}")
        elif choice == "2":
            try:
                interactive_decrypt()
            except (ValueError, UnicodeError) as exc:
                print(f"Ошибка ввода: {exc}")
        else:
            print("Выберите 0, 1 или 2.")
        print()


if __name__ == "__main__":
    interactive_menu()
