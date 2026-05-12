# -*- coding: utf-8 -*-
"""
20. Шифр КУЗНЕЧИК (ГОСТ Р 34.12-2015)

Реализация блочного шифра «Кузнечик».
Блок: 128 бит, ключ: 256 бит, 10 раундов.
Тестирование по ГОСТ Р 34.12-2015 (Приложение А).
"""

PI = [
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135,
    21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177,
    50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87,
    223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3,
    224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74,
    167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
    173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59,
    7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
    225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97,
    32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82,
    89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182,
]

PI_INV = [0] * 256
for i in range(256):
    PI_INV[PI[i]] = i

L_VEC = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]


def gf_mul(a, b):
    p = 0
    hi_bit_set = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        if hi_bit_set:
            a ^= 0x1c3
        a &= 0xff
        b >>= 1
    return p


def S(block):
    return bytes(PI[b] for b in block)


def S_inv(block):
    return bytes(PI_INV[b] for b in block)


def R(block):
    a = 0
    for i in range(16):
        a ^= gf_mul(block[i], L_VEC[i])
    return bytes([a]) + block[:15]


def R_inv(block):
    a = block[0]
    block = block[1:] + bytes([0])
    result = block[:-1] + bytes([0])
    new_last = 0
    for i in range(15):
        new_last ^= gf_mul(result[i], L_VEC[i])
    new_last ^= gf_mul(a, L_VEC[15])
    return result[:15] + bytes([new_last])


def L(block):
    for _ in range(16):
        block = R(block)
    return block


def L_inv(block):
    for _ in range(16):
        block = R_inv(block)
    return block


def F(k, a1, a0):
    tmp = bytes(a ^ b for a, b in zip(k, a1))
    tmp = L(S(tmp))
    return tmp, bytes(a ^ b for a, b in zip(tmp, a0))


def C(i):
    c = bytes([0] * 15 + [i])
    return L(c)


def key_expansion(key):
    k1 = key[:16]
    k2 = key[16:]
    
    round_keys = [k1, k2]
    
    a1, a0 = k1, k2
    for i in range(1, 5):
        for j in range(8):
            c = C(8 * (i - 1) + j + 1)
            a1, a0 = F(c, a1, a0)
        round_keys.extend([a1, a0])
    
    return round_keys


def encrypt_block(block, round_keys):
    state = block
    for i in range(9):
        state = bytes(a ^ b for a, b in zip(state, round_keys[i]))
        state = S(state)
        state = L(state)
    state = bytes(a ^ b for a, b in zip(state, round_keys[9]))
    return state


def decrypt_block(block, round_keys):
    state = block
    state = bytes(a ^ b for a, b in zip(state, round_keys[9]))
    for i in range(8, -1, -1):
        state = L_inv(state)
        state = S_inv(state)
        state = bytes(a ^ b for a, b in zip(state, round_keys[i]))
    return state


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def kuznechik_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    round_keys = key_expansion(key)
    padded = pad_pkcs7(plaintext, 16)
    ciphertext = b''
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        ciphertext += encrypt_block(block, round_keys)
    return ciphertext


def kuznechik_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    round_keys = key_expansion(key)
    plaintext = b''
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        plaintext += decrypt_block(block, round_keys)
    return unpad_pkcs7(plaintext)


def test_gost_vectors():
    print("=" * 70)
    print("ТЕСТ КУЗНЕЧИК по ГОСТ Р 34.12-2015 (Приложение А)")
    print("=" * 70)
    
    key = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    
    plaintext = bytes.fromhex("1122334455667700ffeeddccbbaa9988")
    expected_ciphertext = bytes.fromhex("7f679d90bebc24305a468d42b9d4edcd")
    
    round_keys = key_expansion(key)
    ciphertext = encrypt_block(plaintext, round_keys)
    
    print(f"Ключ (hex): {key.hex()}")
    print(f"Открытый текст: {plaintext.hex()}")
    print(f"Ожидаемый шифртекст: {expected_ciphertext.hex()}")
    print(f"Полученный шифртекст: {ciphertext.hex()}")
    enc_ok = ciphertext == expected_ciphertext
    print(f"Тест шифрования пройден: {'ДА' if enc_ok else 'НЕТ'}")
    
    decrypted = decrypt_block(ciphertext, round_keys)
    print(f"Расшифрованный текст: {decrypted.hex()}")
    dec_ok = decrypted == plaintext
    print(f"Расшифрование верно: {'ДА' if dec_ok else 'НЕТ'}")
    
    print("\nПроверка S-преобразования (А.1.1):")
    s_input = bytes.fromhex("ffeeddccbbaa99881122334455667700")
    s_expected = bytes.fromhex("b66cd8887d38e8d77765aeea0c9a7efc")
    s_result = S(s_input)
    print(f"S({s_input.hex()}) = {s_result.hex()}")
    print(f"Ожидается: {s_expected.hex()}")
    s_ok = s_result == s_expected
    print(f"Тест S пройден: {'ДА' if s_ok else 'НЕТ'}")
    
    print("\nПроверка R-преобразования (А.1.2):")
    r_input = bytes.fromhex("00000000000000000000000000000100")
    r_expected = bytes.fromhex("94000000000000000000000000000001")
    r_result = R(r_input)
    print(f"R({r_input.hex()}) = {r_result.hex()}")
    print(f"Ожидается: {r_expected.hex()}")
    r_ok = r_result == r_expected
    print(f"Тест R пройден: {'ДА' if r_ok else 'НЕТ'}")
    
    print("\nПроверка L-преобразования (А.1.3):")
    l_input = bytes.fromhex("64a59400000000000000000000000000")
    l_expected = bytes.fromhex("d456584dd0e3e84cc3166e4b7fa2890d")
    l_result = L(l_input)
    print(f"L({l_input.hex()}) = {l_result.hex()}")
    print(f"Ожидается: {l_expected.hex()}")
    l_ok = l_result == l_expected
    print(f"Тест L пройден: {'ДА' if l_ok else 'НЕТ'}")
    
    print("=" * 70)
    return enc_ok and dec_ok


def test_long_text():
    print("\n" + "=" * 70)
    print("ТЕСТ НА ТЕКСТЕ 1000+ СИМВОЛОВ")
    print("=" * 70)
    
    long_text = """Криптография — наука о методах обеспечения конфиденциальности, 
целостности данных, аутентификации и невозможности отказа от авторства. 
Шифр «Кузнечик» (ГОСТ Р 34.12-2015) является одним из стандартных 
блочных шифров Российской Федерации. Он использует SP-сеть с 10 раундами, 
размером блока 128 бит и ключом 256 бит.

Шифр «Кузнечик» был разработан для замены устаревшего шифра «Магма» 
(ГОСТ 28147-89) и обеспечивает более высокий уровень безопасности 
благодаря увеличенному размеру блока.

Основные преобразования шифра:
1. S-преобразование (нелинейная подстановка)
2. R-преобразование (линейный сдвиговый регистр)
3. L-преобразование (16-кратное применение R)
4. Сложение с раундовым ключом по модулю 2 (XOR)

Ключевое расписание шифра «Кузнечик» основано на сети Фейстеля 
и использует константы C_i, вычисляемые как L([i]).

Данный алгоритм широко применяется для защиты конфиденциальной информации 
в государственных и коммерческих системах Российской Федерации.

The Kuznyechik cipher is a symmetric block cipher standardized in 
GOST R 34.12-2015. It operates on 128-bit blocks with a 256-bit key 
and uses a substitution-permutation network structure with 10 rounds.
""" * 2
    
    print(f"Длина текста: {len(long_text)} символов")
    
    key = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    
    plaintext_bytes = long_text.encode('utf-8')
    print(f"Длина в байтах: {len(plaintext_bytes)}")
    
    ciphertext = kuznechik_ecb_encrypt(plaintext_bytes, key)
    print(f"Длина шифртекста: {len(ciphertext)} байт")
    print(f"Первые 64 байта шифртекста (hex): {ciphertext[:64].hex()}")
    
    decrypted = kuznechik_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    
    print(f"Расшифрование успешно: {'ДА' if decrypted_text == long_text else 'НЕТ'}")
    print("=" * 70)
    return decrypted_text == long_text


def demo_phrase():
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ НА ФРАЗЕ ВАРИАНТА")
    print("=" * 70)
    
    phrase = "Леопард не может изменить своих пятен"
    print(f"Фраза: {phrase}")
    
    key = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    
    plaintext_bytes = phrase.encode('utf-8')
    ciphertext = kuznechik_ecb_encrypt(plaintext_bytes, key)
    print(f"Шифртекст (hex): {ciphertext.hex()}")
    
    decrypted = kuznechik_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    print(f"Расшифрованный текст: {decrypted_text}")
    print(f"Совпадение: {'ДА' if decrypted_text == phrase else 'НЕТ'}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ШИФР КУЗНЕЧИК (ГОСТ Р 34.12-2015)")
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
