# -*- coding: utf-8 -*-
"""
19. Шифр AES (FIPS-197)

Реализация блочного шифра AES-128/192/256.
Блок: 128 бит, ключ: 128/192/256 бит.
Тестирование по FIPS-197 (Appendix B, C).
"""

S_BOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]

INV_S_BOX = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d,
]

RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]


def xtime(a):
    return (((a << 1) ^ 0x1b) & 0xff) if (a & 0x80) else (a << 1)


def multiply(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = xtime(a)
        b >>= 1
    return result


def sub_bytes(state):
    return [[S_BOX[b] for b in row] for row in state]


def inv_sub_bytes(state):
    return [[INV_S_BOX[b] for b in row] for row in state]


def shift_rows(state):
    return [
        [state[0][0], state[0][1], state[0][2], state[0][3]],
        [state[1][1], state[1][2], state[1][3], state[1][0]],
        [state[2][2], state[2][3], state[2][0], state[2][1]],
        [state[3][3], state[3][0], state[3][1], state[3][2]],
    ]


def inv_shift_rows(state):
    return [
        [state[0][0], state[0][1], state[0][2], state[0][3]],
        [state[1][3], state[1][0], state[1][1], state[1][2]],
        [state[2][2], state[2][3], state[2][0], state[2][1]],
        [state[3][1], state[3][2], state[3][3], state[3][0]],
    ]


def mix_columns(state):
    result = [[0] * 4 for _ in range(4)]
    for c in range(4):
        result[0][c] = multiply(0x02, state[0][c]) ^ multiply(0x03, state[1][c]) ^ state[2][c] ^ state[3][c]
        result[1][c] = state[0][c] ^ multiply(0x02, state[1][c]) ^ multiply(0x03, state[2][c]) ^ state[3][c]
        result[2][c] = state[0][c] ^ state[1][c] ^ multiply(0x02, state[2][c]) ^ multiply(0x03, state[3][c])
        result[3][c] = multiply(0x03, state[0][c]) ^ state[1][c] ^ state[2][c] ^ multiply(0x02, state[3][c])
    return result


def inv_mix_columns(state):
    result = [[0] * 4 for _ in range(4)]
    for c in range(4):
        result[0][c] = multiply(0x0e, state[0][c]) ^ multiply(0x0b, state[1][c]) ^ multiply(0x0d, state[2][c]) ^ multiply(0x09, state[3][c])
        result[1][c] = multiply(0x09, state[0][c]) ^ multiply(0x0e, state[1][c]) ^ multiply(0x0b, state[2][c]) ^ multiply(0x0d, state[3][c])
        result[2][c] = multiply(0x0d, state[0][c]) ^ multiply(0x09, state[1][c]) ^ multiply(0x0e, state[2][c]) ^ multiply(0x0b, state[3][c])
        result[3][c] = multiply(0x0b, state[0][c]) ^ multiply(0x0d, state[1][c]) ^ multiply(0x09, state[2][c]) ^ multiply(0x0e, state[3][c])
    return result


def add_round_key(state, round_key):
    return [[state[r][c] ^ round_key[r][c] for c in range(4)] for r in range(4)]


def key_expansion(key):
    key_len = len(key)
    if key_len == 16:
        nk = 4
        nr = 10
    elif key_len == 24:
        nk = 6
        nr = 12
    elif key_len == 32:
        nk = 8
        nr = 14
    else:
        raise ValueError("Invalid key length")
    
    w = []
    for i in range(nk):
        w.append([key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]])
    
    for i in range(nk, 4 * (nr + 1)):
        temp = w[i-1][:]
        if i % nk == 0:
            temp = [S_BOX[temp[1]], S_BOX[temp[2]], S_BOX[temp[3]], S_BOX[temp[0]]]
            temp[0] ^= RCON[(i // nk) - 1]
        elif nk > 6 and i % nk == 4:
            temp = [S_BOX[b] for b in temp]
        w.append([w[i-nk][j] ^ temp[j] for j in range(4)])
    
    round_keys = []
    for r in range(nr + 1):
        rk = [[w[4*r + c][row] for c in range(4)] for row in range(4)]
        round_keys.append(rk)
    
    return round_keys, nr


def bytes_to_state(block):
    return [[block[r + 4*c] for c in range(4)] for r in range(4)]


def state_to_bytes(state):
    return bytes([state[r][c] for c in range(4) for r in range(4)])


def aes_encrypt_block(plaintext, key):
    state = bytes_to_state(plaintext)
    round_keys, nr = key_expansion(key)
    
    state = add_round_key(state, round_keys[0])
    
    for r in range(1, nr):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[r])
    
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[nr])
    
    return state_to_bytes(state)


def aes_decrypt_block(ciphertext, key):
    state = bytes_to_state(ciphertext)
    round_keys, nr = key_expansion(key)
    
    state = add_round_key(state, round_keys[nr])
    
    for r in range(nr - 1, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, round_keys[r])
        state = inv_mix_columns(state)
    
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, round_keys[0])
    
    return state_to_bytes(state)


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def aes_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    padded = pad_pkcs7(plaintext, 16)
    ciphertext = b''
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        ciphertext += aes_encrypt_block(block, key)
    return ciphertext


def aes_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    plaintext = b''
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        plaintext += aes_decrypt_block(block, key)
    return unpad_pkcs7(plaintext)


def test_fips197():
    print("=" * 70)
    print("ТЕСТ AES по FIPS-197")
    print("=" * 70)
    
    print("\nТест AES-128 (Appendix B):")
    key_128 = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    plaintext = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
    expected_128 = bytes.fromhex("3925841d02dc09fbdc118597196a0b32")
    
    ciphertext_128 = aes_encrypt_block(plaintext, key_128)
    print(f"Ключ: {key_128.hex()}")
    print(f"Открытый текст: {plaintext.hex()}")
    print(f"Ожидаемый шифртекст: {expected_128.hex()}")
    print(f"Полученный шифртекст: {ciphertext_128.hex()}")
    test_128_ok = ciphertext_128 == expected_128
    print(f"Тест пройден: {'ДА' if test_128_ok else 'НЕТ'}")
    
    decrypted = aes_decrypt_block(ciphertext_128, key_128)
    print(f"Расшифрованный: {decrypted.hex()}")
    print(f"Расшифрование верно: {'ДА' if decrypted == plaintext else 'НЕТ'}")
    
    print("\nТест AES-128 (Appendix C.1):")
    key_c1 = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    plaintext_c1 = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected_c1 = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")
    
    ciphertext_c1 = aes_encrypt_block(plaintext_c1, key_c1)
    print(f"Ключ: {key_c1.hex()}")
    print(f"Открытый текст: {plaintext_c1.hex()}")
    print(f"Ожидаемый шифртекст: {expected_c1.hex()}")
    print(f"Полученный шифртекст: {ciphertext_c1.hex()}")
    test_c1_ok = ciphertext_c1 == expected_c1
    print(f"Тест пройден: {'ДА' if test_c1_ok else 'НЕТ'}")
    
    print("\nТест AES-192 (Appendix C.2):")
    key_192 = bytes.fromhex("000102030405060708090a0b0c0d0e0f1011121314151617")
    plaintext_192 = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected_192 = bytes.fromhex("dda97ca4864cdfe06eaf70a0ec0d7191")
    
    ciphertext_192 = aes_encrypt_block(plaintext_192, key_192)
    print(f"Ключ: {key_192.hex()}")
    print(f"Открытый текст: {plaintext_192.hex()}")
    print(f"Ожидаемый шифртекст: {expected_192.hex()}")
    print(f"Полученный шифртекст: {ciphertext_192.hex()}")
    test_192_ok = ciphertext_192 == expected_192
    print(f"Тест пройден: {'ДА' if test_192_ok else 'НЕТ'}")
    
    print("\nТест AES-256 (Appendix C.3):")
    key_256 = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    plaintext_256 = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected_256 = bytes.fromhex("8ea2b7ca516745bfeafc49904b496089")
    
    ciphertext_256 = aes_encrypt_block(plaintext_256, key_256)
    print(f"Ключ: {key_256.hex()}")
    print(f"Открытый текст: {plaintext_256.hex()}")
    print(f"Ожидаемый шифртекст: {expected_256.hex()}")
    print(f"Полученный шифртекст: {ciphertext_256.hex()}")
    test_256_ok = ciphertext_256 == expected_256
    print(f"Тест пройден: {'ДА' if test_256_ok else 'НЕТ'}")
    
    print("=" * 70)
    return test_128_ok and test_c1_ok and test_192_ok and test_256_ok


def test_long_text():
    print("\n" + "=" * 70)
    print("ТЕСТ НА ТЕКСТЕ 1000+ СИМВОЛОВ")
    print("=" * 70)
    
    long_text = """Advanced Encryption Standard (AES) is a specification for the encryption 
of electronic data established by the U.S. National Institute of Standards 
and Technology (NIST) in 2001. AES is a variant of Rijndael, with a fixed 
block size of 128 bits, and a key size of 128, 192, or 256 bits.

AES operates on a 4x4 column-major order array of bytes, termed the state. 
Most AES calculations are done in a particular finite field. For a 128-bit 
key, there are 10 rounds of processing, while 192-bit and 256-bit keys 
require 12 and 14 rounds respectively.

Each round consists of several processing steps:
1. SubBytes - a non-linear substitution step
2. ShiftRows - a transposition step
3. MixColumns - a linear mixing operation
4. AddRoundKey - each byte combined with round key using XOR

The AES algorithm is considered secure and is widely used worldwide. 
It has been adopted by the U.S. government and is now used worldwide 
to protect classified information.

Криптография — наука о методах обеспечения конфиденциальности, 
целостности данных, аутентификации и невозможности отказа от авторства.
Шифр AES является одним из наиболее распространенных симметричных 
блочных шифров в мире.
""" * 2
    
    print(f"Длина текста: {len(long_text)} символов")
    
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    
    plaintext_bytes = long_text.encode('utf-8')
    print(f"Длина в байтах: {len(plaintext_bytes)}")
    
    ciphertext = aes_ecb_encrypt(plaintext_bytes, key)
    print(f"Длина шифртекста: {len(ciphertext)} байт")
    print(f"Первые 64 байта шифртекста (hex): {ciphertext[:64].hex()}")
    
    decrypted = aes_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    
    print(f"Расшифрование успешно: {'ДА' if decrypted_text == long_text else 'НЕТ'}")
    print("=" * 70)
    return decrypted_text == long_text


def demo_phrase():
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ НА ФРАЗЕ")
    print("=" * 70)
    
    phrase = "Леопард не может изменить своих пятен"
    print(f"Фраза: {phrase}")
    
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    
    plaintext_bytes = phrase.encode('utf-8')
    ciphertext = aes_ecb_encrypt(plaintext_bytes, key)
    print(f"Шифртекст (hex): {ciphertext.hex()}")
    
    decrypted = aes_ecb_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    print(f"Расшифрованный текст: {decrypted_text}")
    print(f"Совпадение: {'ДА' if decrypted_text == phrase else 'НЕТ'}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ШИФР AES (FIPS-197)")
    print("=" * 70)
    
    fips_ok = test_fips197()
    long_ok = test_long_text()
    demo_phrase()
    
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"Тест FIPS-197: {'ПРОЙДЕН' if fips_ok else 'НЕ ПРОЙДЕН'}")
    print(f"Тест 1000+ символов: {'ПРОЙДЕН' if long_ok else 'НЕ ПРОЙДЕН'}")
    print("=" * 70)
