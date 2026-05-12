# -*- coding: utf-8 -*-
"""
18. ГОСТ 28147-89 — режим простой замены

Отладка и тестирование программы по тесту ГОСТ Р 34.12-2015 («МАГМА»).
ГОСТ 28147-89 является предшественником шифра МАГМА.
Тестирование с использованием S-блоков из ГОСТ Р 34.12-2015.
"""

import struct

DEFAULT_PHRASE = "Леопард не может изменить своих пятен"

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


def rotl32(x, n):
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def round_function(k, a):
    x = (a + k) & 0xFFFFFFFF
    x = t_direct(x)
    return rotl32(x, 11)


def round_keys_from_key(key32: bytes):
    if len(key32) != 32:
        raise ValueError("Ключ должен быть 32 байта (256 бит)")
    K = [int.from_bytes(key32[4 * i : 4 * (i + 1)], "little") for i in range(8)]
    rk = []
    for i in range(32):
        if i < 24:
            rk.append(K[i % 8])
        else:
            rk.append(K[7 - (i - 24)])
    return rk


def encrypt_block(block: bytes, rk) -> bytes:
    n1 = int.from_bytes(block[0:4], "little")
    n2 = int.from_bytes(block[4:8], "little")
    
    for i in range(31):
        tmp = round_function(rk[i], n1)
        tmp = tmp ^ n2
        n2 = n1
        n1 = tmp
    
    tmp = round_function(rk[31], n1)
    n2 = tmp ^ n2
    
    return n1.to_bytes(4, "little") + n2.to_bytes(4, "little")


def decrypt_block(block: bytes, rk) -> bytes:
    n1 = int.from_bytes(block[0:4], "little")
    n2 = int.from_bytes(block[4:8], "little")
    
    tmp = round_function(rk[31], n1)
    n2 = tmp ^ n2
    
    for i in range(30, -1, -1):
        tmp = n1
        n1 = n2
        n2 = tmp
        tmp = round_function(rk[i], n1)
        n2 = tmp ^ n2
    
    return n1.to_bytes(4, "little") + n2.to_bytes(4, "little")


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def gost_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    padded = pad_pkcs7(plaintext, 8)
    ciphertext = b''
    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        ciphertext += encrypt_block(block, rk)
    return ciphertext


def gost_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    plaintext = b''
    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i:i+8]
        plaintext += decrypt_block(block, rk)
    return unpad_pkcs7(plaintext)


def test_gost_r_34_12_2015():
    print("=" * 70)
    print("ТЕСТ ГОСТ 28147-89 по тесту ГОСТ Р 34.12-2015 (МАГМА)")
    print("=" * 70)
    
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    
    plaintext = bytes.fromhex("fedcba9876543210")
    expected_ciphertext = bytes.fromhex("4ee901e5c2d8ca3d")
    
    rk = round_keys_from_key(key)
    ciphertext = encrypt_block(plaintext, rk)
    
    print(f"Ключ (hex): {key.hex()}")
    print(f"Открытый текст: {plaintext.hex()}")
    print(f"Ожидаемый шифртекст (ГОСТ Р 34.12-2015): {expected_ciphertext.hex()}")
    print(f"Полученный шифртекст: {ciphertext.hex()}")
    enc_ok = ciphertext == expected_ciphertext
    print(f"Тест пройден: {'ДА' if enc_ok else 'НЕТ'}")
    
    decrypted = decrypt_block(ciphertext, rk)
    print(f"Расшифрованный текст: {decrypted.hex()}")
    dec_ok = decrypted == plaintext
    print(f"Расшифрование верно: {'ДА' if dec_ok else 'НЕТ'}")
    
    print("\n" + "-" * 70)
    print("Тестовые векторы S-преобразования (RFC 8891, Приложение A.1):")
    s_tests = [
        (0xFDB97531, 0x2A196F34),
        (0x2A196F34, 0xEBD9F03A),
        (0xEBD9F03A, 0xB039BB3D),
        (0xB039BB3D, 0x68695433),
    ]
    
    for inp, expected in s_tests:
        result = t_direct(inp)
        ok = result == expected
        print(f"t(0x{inp:08X}) = 0x{result:08X} (ожид. 0x{expected:08X}) - {'OK' if ok else 'FAIL'}")
    
    print("=" * 70)
    return enc_ok and dec_ok


def test_long_text():
    print("\n" + "=" * 70)
    print("ТЕСТ НА ТЕКСТЕ 1000+ СИМВОЛОВ")
    print("=" * 70)
    
    long_text = """ГОСТ 28147-89 — советский и российский стандарт симметричного 
шифрования, введённый в 1990 году. Этот стандарт является обязательным 
для применения в государственных организациях и часто используется в 
коммерческих системах.

Алгоритм использует сеть Фейстеля с 32 раундами и размером блока 64 бита.
Длина ключа составляет 256 бит, что обеспечивает высокую криптостойкость.

Основные особенности ГОСТ 28147-89:
1. Блочный шифр с размером блока 64 бита
2. Ключ длиной 256 бит
3. 32 раунда шифрования
4. Использует таблицы замены (S-блоки)
5. Поддерживает различные режимы работы

В 2015 году был введён ГОСТ Р 34.12-2015, который определяет 
фиксированные S-блоки для алгоритма «Магма» (модификация ГОСТ 28147-89).

Данная реализация использует S-блоки из ГОСТ Р 34.12-2015 для обеспечения 
совместимости с современным стандартом и возможности тестирования 
по официальным тестовым векторам.

Криптография играет важную роль в обеспечении безопасности 
информационных систем и защите персональных данных.
""" * 2
    
    print(f"Длина текста: {len(long_text)} символов")
    
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    
    plaintext_bytes = long_text.encode('utf-8')
    print(f"Длина в байтах: {len(plaintext_bytes)}")
    
    ciphertext = gost_ecb_encrypt(plaintext_bytes, key)
    print(f"Длина шифртекста: {len(ciphertext)} байт")
    print(f"Первые 64 байта шифртекста (hex): {ciphertext[:64].hex()}")
    
    decrypted = gost_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    
    print(f"Расшифрование успешно: {'ДА' if decrypted_text == long_text else 'НЕТ'}")
    print("=" * 70)
    return decrypted_text == long_text


def demo_phrase():
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ НА ФРАЗЕ ВАРИАНТА")
    print("=" * 70)
    
    phrase = DEFAULT_PHRASE
    print(f"Фраза: {phrase}")
    
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    
    plaintext_bytes = phrase.encode('utf-8')
    ciphertext = gost_ecb_encrypt(plaintext_bytes, key)
    print(f"Шифртекст (hex): {ciphertext.hex()}")
    
    decrypted = gost_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    print(f"Расшифрованный текст: {decrypted_text}")
    print(f"Совпадение: {'ДА' if decrypted_text == phrase else 'НЕТ'}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ГОСТ 28147-89 — РЕЖИМ ПРОСТОЙ ЗАМЕНЫ")
    print("Тестирование по ГОСТ Р 34.12-2015 (МАГМА)")
    print("=" * 70)
    
    gost_ok = test_gost_r_34_12_2015()
    long_ok = test_long_text()
    demo_phrase()
    
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"Тест ГОСТ Р 34.12-2015: {'ПРОЙДЕН' if gost_ok else 'НЕ ПРОЙДЕН'}")
    print(f"Тест 1000+ символов: {'ПРОЙДЕН' if long_ok else 'НЕ ПРОЙДЕН'}")
    print("=" * 70)
