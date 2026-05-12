# -*- coding: utf-8 -*-
"""
14. Гаммирование ГОСТ Р 34.13-2015 (МАГМА)

Реализован режим гаммирования (CTR) по ГОСТ Р 34.13-2015 с использованием
блочного шифра «Магма» (ГОСТ Р 34.12-2015).

Режим гаммирования:
- Вектор инициализации (IV) шифруется блочным шифром для получения гаммы
- Гамма XOR-ится с открытым текстом для получения шифртекста
- Для следующего блока IV инкрементируется

Параметры:
- Блок: 64 бита (8 байт)
- Ключ: 256 бит (32 байта)
- IV: 64 бита (8 байт)
"""

import struct
import os

DEFAULT_PHRASE = "Леопард не может изменить своих пятен"

DEFAULT_KEY_HEX = (
    "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
)

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


def round_keys_from_key(key32: bytes):
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
    for i in range(31):
        a1, a0 = G_feistel(rk[i], a1, a0)
    k = rk[31]
    out1 = (g_round(k, a0) ^ a1) & 0xFFFFFFFF
    out0 = a0 & 0xFFFFFFFF
    return out1, out0


def pack64(a1: int, a0: int) -> bytes:
    return a1.to_bytes(4, "big") + a0.to_bytes(4, "big")


def unpack64(block8: bytes) -> tuple:
    if len(block8) != 8:
        raise ValueError("Блок должен быть 8 байт")
    a1 = int.from_bytes(block8[0:4], "big")
    a0 = int.from_bytes(block8[4:8], "big")
    return a1, a0


def increment_iv(iv_bytes: bytes) -> bytes:
    val = int.from_bytes(iv_bytes, "big")
    val = (val + 1) % (2 ** 64)
    return val.to_bytes(8, "big")


def gamma_encrypt(plaintext: bytes, key32: bytes, iv: bytes) -> bytes:
    """
    Гаммирование (CTR режим) по ГОСТ Р 34.13-2015.
    
    Генерирует гамму путём шифрования счётчика (IV) блочным шифром МАГМА,
    затем XOR-ит гамму с открытым текстом.
    """
    if len(iv) != 8:
        raise ValueError("IV должен быть 8 байт (64 бита)")
    
    rk = round_keys_from_key(key32)
    result = bytearray()
    current_iv = iv
    
    for i in range(0, len(plaintext), 8):
        block = plaintext[i:i+8]
        
        iv_a1, iv_a0 = unpack64(current_iv)
        gamma_a1, gamma_a0 = encrypt_block_magma(iv_a1, iv_a0, rk)
        gamma_block = pack64(gamma_a1, gamma_a0)
        
        for j in range(len(block)):
            result.append(block[j] ^ gamma_block[j])
        
        current_iv = increment_iv(current_iv)
    
    return bytes(result)


def gamma_decrypt(ciphertext: bytes, key32: bytes, iv: bytes) -> bytes:
    """
    Расшифрование гаммирования — идентично шифрованию (XOR симметричен).
    """
    return gamma_encrypt(ciphertext, key32, iv)


def gamma_encrypt_text(plaintext: str, key32: bytes, iv: bytes) -> tuple:
    """
    Шифрует текстовую строку с сохранением информации о длине.
    Возвращает (шифртекст, IV).
    """
    raw = plaintext.encode("utf-8")
    n = len(raw)
    body = struct.pack(">I", n) + raw
    pad = (8 - len(body) % 8) % 8
    body = body + bytes(pad)
    
    ciphertext = gamma_encrypt(body, key32, iv)
    return ciphertext, iv


def gamma_decrypt_text(ciphertext: bytes, key32: bytes, iv: bytes) -> str:
    """
    Расшифровывает текст, зашифрованный gamma_encrypt_text.
    """
    plainbytes = gamma_decrypt(ciphertext, key32, iv)
    n = struct.unpack(">I", plainbytes[:4])[0]
    return plainbytes[4:4+n].decode("utf-8")


def parse_key_hex(hex_str: str) -> bytes:
    s = hex_str.strip().replace(" ", "")
    if len(s) != 64:
        raise ValueError("Ключ: ровно 64 шестнадцатеричных символа (256 бит)")
    return bytes.fromhex(s)


def generate_iv() -> bytes:
    return os.urandom(8)


def _print_demo(phrase: str, key32: bytes, iv: bytes):
    print("=" * 70)
    print("Гаммирование ГОСТ Р 34.13-2015 (МАГМА)")
    print("=" * 70)
    print(f"Исходный текст ({len(phrase)} символов):")
    if len(phrase) > 100:
        print(f"  {phrase[:100]}...")
    else:
        print(f"  {phrase}")
    print(f"Ключ (hex): {key32.hex()}")
    print(f"IV (hex): {iv.hex()}")
    print("-" * 70)
    
    ciphertext, _ = gamma_encrypt_text(phrase, key32, iv)
    print(f"Шифртекст ({len(ciphertext)} байт, hex):")
    if len(ciphertext) > 64:
        print(f"  {ciphertext[:64].hex()}...")
    else:
        print(f"  {ciphertext.hex()}")
    
    decrypted = gamma_decrypt_text(ciphertext, key32, iv)
    print("-" * 70)
    print(f"Расшифрованный текст ({len(decrypted)} символов):")
    if len(decrypted) > 100:
        print(f"  {decrypted[:100]}...")
    else:
        print(f"  {decrypted}")
    print(f"Совпадение с исходным: {'ДА' if decrypted == phrase else 'НЕТ'}")
    print("=" * 70)


def _test_1000_chars():
    test_text = """Криптография — наука о методах обеспечения конфиденциальности, целостности данных, 
аутентификации, шифрования. Шифр МАГМА (ГОСТ Р 34.12-2015) является российским стандартом 
блочного шифрования с размером блока 64 бита и ключом 256 бит. Режим гаммирования (CTR) 
позволяет превратить блочный шифр в поточный, генерируя псевдослучайную гамму путём 
шифрования последовательных значений счётчика. Гамма затем XOR-ится с открытым текстом.

Преимущества режима CTR:
1. Параллельная обработка блоков
2. Произвольный доступ к блокам
3. Предварительное вычисление гаммы
4. Отсутствие необходимости в дополнении

ГОСТ Р 34.13-2015 определяет режимы работы для блочных шифров МАГМА и Кузнечик.
Стандарт описывает режимы: ECB, CBC, CFB, OFB, CTR, а также режим гаммирования с обратной связью.

Сеть Фейстеля — конструкция, лежащая в основе многих блочных шифров, включая DES и МАГМА.
В сети Фейстеля блок данных делится на две половины, и в каждом раунде одна половина 
преобразуется с помощью раундовой функции и XOR-ится с другой половиной.

Данный текст содержит более тысячи символов и используется для тестирования корректности
реализации алгоритма гаммирования по ГОСТ Р 34.13-2015 с использованием шифра МАГМА."""
    
    print("\n" + "=" * 70)
    print("ТЕСТ: Шифрование текста длиной более 1000 символов")
    print("=" * 70)
    print(f"Длина тестового текста: {len(test_text)} символов")
    
    key32 = parse_key_hex(DEFAULT_KEY_HEX)
    iv = bytes.fromhex("1234567890abcdef")
    
    ciphertext, _ = gamma_encrypt_text(test_text, key32, iv)
    print(f"Длина шифртекста: {len(ciphertext)} байт")
    
    decrypted = gamma_decrypt_text(ciphertext, key32, iv)
    
    success = decrypted == test_text
    print(f"Расшифрование успешно: {'ДА' if success else 'НЕТ'}")
    print(f"Длина расшифрованного текста: {len(decrypted)} символов")
    
    if success:
        print("\nТЕСТ ПРОЙДЕН: Текст более 1000 символов успешно зашифрован и расшифрован!")
    else:
        print("\nТЕСТ НЕ ПРОЙДЕН: Расшифрованный текст не совпадает с оригиналом!")
    
    print("=" * 70)
    return success


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

    print("IV 64 бита, 16 hex-символов (Enter — случайный IV): ", end="")
    try:
        iv_in = input().strip()
    except EOFError:
        iv_in = ""
    
    if iv_in:
        try:
            iv = bytes.fromhex(iv_in.replace(" ", ""))
            if len(iv) != 8:
                raise ValueError("IV должен быть 8 байт")
        except ValueError as e:
            print(f"Ошибка IV: {e}")
            iv = generate_iv()
            print(f"Сгенерирован случайный IV: {iv.hex()}")
    else:
        iv = generate_iv()
        print(f"Сгенерирован случайный IV: {iv.hex()}")

    _print_demo(phrase, key32, iv)
    
    _test_1000_chars()
