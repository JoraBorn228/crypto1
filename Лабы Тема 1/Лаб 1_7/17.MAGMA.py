# -*- coding: utf-8 -*-
"""
17. Шифр МАГМА (ГОСТ Р 34.12-2015)

Реализация блочного шифра «Магма» с режимом ECB.
Блок: 64 бита, ключ: 256 бит, 32 раунда.
Тестирование по ГОСТ Р 34.12-2015 (Приложение А).
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


def g_round(k, a):
    x = (a + k) & 0xFFFFFFFF
    x = t_direct(x)
    return rotl32(x, 11)


def G_feistel(k, a1, a0):
    return a0 & 0xFFFFFFFF, (g_round(k, a0) ^ a1) & 0xFFFFFFFF


def inv_G_feistel(k, new_a1, new_a0):
    old_a0 = new_a1
    old_a1 = (g_round(k, new_a1) ^ new_a0) & 0xFFFFFFFF
    return old_a1, old_a0


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


def encrypt_block_magma(block: bytes, rk) -> bytes:
    a0 = int.from_bytes(block[0:4], "little")
    a1 = int.from_bytes(block[4:8], "little")
    for i in range(31):
        a1, a0 = G_feistel(rk[i], a1, a0)
    k = rk[31]
    out1 = (g_round(k, a0) ^ a1) & 0xFFFFFFFF
    out0 = a0 & 0xFFFFFFFF
    return out0.to_bytes(4, "little") + out1.to_bytes(4, "little")


def decrypt_block_magma(block: bytes, rk) -> bytes:
    a0 = int.from_bytes(block[0:4], "little")
    a1 = int.from_bytes(block[4:8], "little")
    a1_temp = (g_round(rk[31], a0) ^ a1) & 0xFFFFFFFF
    a0_temp = a0
    a1, a0 = a1_temp, a0_temp
    for i in range(30, -1, -1):
        a1, a0 = inv_G_feistel(rk[i], a1, a0)
    return a0.to_bytes(4, "little") + a1.to_bytes(4, "little")


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def magma_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    padded = pad_pkcs7(plaintext, 8)
    ciphertext = b''
    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        ciphertext += encrypt_block_magma(block, rk)
    return ciphertext


def magma_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    rk = round_keys_from_key(key)
    plaintext = b''
    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i:i+8]
        plaintext += decrypt_block_magma(block, rk)
    return unpad_pkcs7(plaintext)


def test_gost_vectors():
    print("=" * 70)
    print("ТЕСТ МАГМА по ГОСТ Р 34.12-2015 (Приложение А)")
    print("=" * 70)
    
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    
    plaintext = bytes.fromhex("fedcba9876543210")
    expected_ciphertext = bytes.fromhex("4ee901e5c2d8ca3d")
    
    rk = round_keys_from_key(key)
    ciphertext = encrypt_block_magma(plaintext, rk)
    
    print(f"Ключ (hex): {key.hex()}")
    print(f"Открытый текст: {plaintext.hex()}")
    print(f"Ожидаемый шифртекст: {expected_ciphertext.hex()}")
    print(f"Полученный шифртекст: {ciphertext.hex()}")
    print(f"Тест пройден: {'ДА' if ciphertext == expected_ciphertext else 'НЕТ'}")
    
    decrypted = decrypt_block_magma(ciphertext, rk)
    print(f"Расшифрованный текст: {decrypted.hex()}")
    print(f"Расшифрование верно: {'ДА' if decrypted == plaintext else 'НЕТ'}")
    print("=" * 70)
    return ciphertext == expected_ciphertext and decrypted == plaintext


def test_long_text():
    print("\n" + "=" * 70)
    print("ТЕСТ НА ТЕКСТЕ 1000+ СИМВОЛОВ")
    print("=" * 70)
    
    long_text = """Криптография — наука о методах обеспечения конфиденциальности, 
целостности данных, аутентификации и невозможности отказа от авторства. 
Шифр МАГМА (ГОСТ Р 34.12-2015) является одним из стандартных блочных шифров 
Российской Федерации. Он использует сеть Фейстеля с 32 раундами, 
размером блока 64 бита и ключом 256 бит. Шифр МАГМА основан на 
ГОСТ 28147-89, но использует фиксированные S-блоки. 

Данный алгоритм широко применяется для защиты конфиденциальной информации 
в государственных и коммерческих системах. Блочные шифры являются основой 
современной симметричной криптографии и используются во многих протоколах 
защиты информации.

Сеть Фейстеля — это структура, используемая в большинстве блочных шифров. 
Она позволяет строить обратимые преобразования из необратимых функций. 
В каждом раунде одна половина блока преобразуется с помощью раундовой функции 
и ключа, а затем складывается с другой половиной по модулю 2 (XOR).

Важной особенностью шифра МАГМА является использование нелинейных 
S-блоков (таблиц замены), которые обеспечивают стойкость к линейному 
и дифференциальному криптоанализу. Каждый S-блок представляет собой 
биективное отображение 4-битного входа в 4-битный выход.

Режим ECB (Electronic Codebook) — простейший режим работы блочного шифра, 
в котором каждый блок шифруется независимо. Этот режим используется 
для тестирования и отладки, но не рекомендуется для реального применения 
из-за уязвимости к анализу шаблонов.
""" * 2
    
    print(f"Длина текста: {len(long_text)} символов")
    
    key = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    
    plaintext_bytes = long_text.encode('utf-8')
    print(f"Длина в байтах: {len(plaintext_bytes)}")
    
    ciphertext = magma_ecb_encrypt(plaintext_bytes, key)
    print(f"Длина шифртекста: {len(ciphertext)} байт")
    print(f"Первые 64 байта шифртекста (hex): {ciphertext[:64].hex()}")
    
    decrypted = magma_ecb_decrypt(ciphertext, key)
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
    ciphertext = magma_ecb_encrypt(plaintext_bytes, key)
    print(f"Шифртекст (hex): {ciphertext.hex()}")
    
    decrypted = magma_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    print(f"Расшифрованный текст: {decrypted_text}")
    print(f"Совпадение: {'ДА' if decrypted_text == phrase else 'НЕТ'}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ШИФР МАГМА (ГОСТ Р 34.12-2015)")
    print("=" * 70)
    
    gost_ok = test_gost_vectors()
    long_ok = test_long_text()
    demo_phrase()
    
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"Тест ГОСТ: {'ПРОЙДЕН' if gost_ok else 'НЕ ПРОЙДЕН'}")
    print(f"Тест 1000+ символов: {'ПРОЙДЕН' if long_ok else 'НЕ ПРОЙДЕН'}")
    print("=" * 70)
