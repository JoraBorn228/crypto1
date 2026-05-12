"""
ПОТОЧНЫЙ ШИФР A5/2
Упрощённая версия A5/1, используемая в GSM для экспортных регионов.
Содержит 4 LFSR (3 основных + 1 управляющий).
"""

class LFSR:
    def __init__(self, size, taps):
        self.size = size
        self.taps = taps
        self.register = [0] * size

    def set_register(self, bits):
        for i in range(min(len(bits), self.size)):
            self.register[i] = bits[i]

    def clock(self):
        feedback = 0
        for tap in self.taps:
            feedback ^= self.register[tap]
        output = self.register[-1]
        self.register = [feedback] + self.register[:-1]
        return output

    def get_bit(self, position):
        return self.register[position]

    def get_output(self):
        return self.register[-1]


class A5_2:
    def __init__(self):
        self.r1 = LFSR(19, [18, 17, 16, 13])
        self.r2 = LFSR(22, [21, 20])
        self.r3 = LFSR(23, [22, 21, 20, 7])
        self.r4 = LFSR(17, [16, 11])

    def majority(self, x, y, z):
        return (x & y) | (x & z) | (y & z)

    def clock_registers(self):
        maj = self.majority(
            self.r4.get_bit(3),
            self.r4.get_bit(7),
            self.r4.get_bit(10)
        )

        if self.r4.get_bit(3) == maj:
            self.r1.clock()
        if self.r4.get_bit(7) == maj:
            self.r2.clock()
        if self.r4.get_bit(10) == maj:
            self.r3.clock()

        self.r4.clock()

    def get_output_bit(self):
        x = self.r1.get_output()
        y = self.r2.get_output()
        z = self.r3.get_output()

        a = self.r1.get_bit(15)
        b = self.r2.get_bit(16)
        c = self.r3.get_bit(13)

        maj = self.majority(a, b, c)
        output = x ^ y ^ z ^ maj
        return output

    def initialize(self, key, frame_number):
        key_bits = []
        for byte in key:
            for i in range(8):
                key_bits.append((byte >> i) & 1)

        while len(key_bits) < 64:
            key_bits.append(0)

        frame_bits = []
        for i in range(22):
            frame_bits.append((frame_number >> i) & 1)

        self.r1.register = [0] * 19
        self.r2.register = [0] * 22
        self.r3.register = [0] * 23
        self.r4.register = [0] * 17

        for i in range(64):
            bit = key_bits[i]
            self.r1.register[0] ^= bit
            self.r2.register[0] ^= bit
            self.r3.register[0] ^= bit
            self.r4.register[0] ^= bit
            self.r1.clock()
            self.r2.clock()
            self.r3.clock()
            self.r4.clock()

        for i in range(22):
            bit = frame_bits[i]
            self.r1.register[0] ^= bit
            self.r2.register[0] ^= bit
            self.r3.register[0] ^= bit
            self.r4.register[0] ^= bit
            self.r1.clock()
            self.r2.clock()
            self.r3.clock()
            self.r4.clock()

        self.r1.register[15] = 1
        self.r2.register[16] = 1
        self.r3.register[18] = 1
        self.r4.register[10] = 1

        for _ in range(99):
            self.clock_registers()

    def generate_keystream(self, length):
        keystream = []
        for _ in range(length):
            self.clock_registers()
            keystream.append(self.get_output_bit())
        return keystream


def text_to_bits(text):
    bits = []
    encoded = text.encode('utf-8')
    for byte in encoded:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


def bits_to_text(bits):
    while len(bits) % 8 != 0:
        bits.append(0)
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        bytes_list.append(byte)
    try:
        return bytes(bytes_list).decode('utf-8', errors='replace')
    except:
        return bytes(bytes_list).decode('latin-1')


def bits_to_hex(bits):
    hex_str = ""
    for i in range(0, len(bits), 4):
        nibble = 0
        for j in range(4):
            if i + j < len(bits):
                nibble = (nibble << 1) | bits[i + j]
            else:
                nibble = nibble << 1
        hex_str += format(nibble, 'X')
    return hex_str


def encrypt(text, key_hex, frame_number=0):
    key = bytes.fromhex(key_hex.replace(" ", ""))
    if len(key) < 8:
        key = key + bytes(8 - len(key))
    key = key[:8]

    cipher = A5_2()
    cipher.initialize(key, frame_number)

    plaintext_bits = text_to_bits(text)
    keystream = cipher.generate_keystream(len(plaintext_bits))

    ciphertext_bits = []
    for i in range(len(plaintext_bits)):
        ciphertext_bits.append(plaintext_bits[i] ^ keystream[i])

    return ciphertext_bits, keystream


def decrypt(ciphertext_bits, key_hex, frame_number=0):
    key = bytes.fromhex(key_hex.replace(" ", ""))
    if len(key) < 8:
        key = key + bytes(8 - len(key))
    key = key[:8]

    cipher = A5_2()
    cipher.initialize(key, frame_number)

    keystream = cipher.generate_keystream(len(ciphertext_bits))

    plaintext_bits = []
    for i in range(len(ciphertext_bits)):
        plaintext_bits.append(ciphertext_bits[i] ^ keystream[i])

    return bits_to_text(plaintext_bits)


if __name__ == "__main__":
    print("=" * 60)
    print("ПОТОЧНЫЙ ШИФР A5/2")
    print("=" * 60)

    print("\nВыберите режим:")
    print("1 - Использовать фразу по умолчанию")
    print("2 - Ввести свой текст")
    choice = input("Ваш выбор (1/2): ").strip()

    if choice == "2":
        original = input("Введите текст для шифрования: ")
    else:
        original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

    print("\nВведите ключ (8 байт в hex, например: 0102030405060708)")
    print("Или нажмите Enter для ключа по умолчанию")
    key_input = input("Ключ: ").strip()
    if not key_input:
        key_hex = "0102030405060708"
    else:
        key_hex = key_input

    print("\nВведите номер кадра (число, по умолчанию 0):")
    frame_input = input("Номер кадра: ").strip()
    if frame_input:
        frame_number = int(frame_input)
    else:
        frame_number = 0

    print("\n" + "-" * 60)
    print(f"Исходный текст: {original}")
    print(f"Ключ: {key_hex}")
    print(f"Номер кадра: {frame_number}")
    print("-" * 60)

    ciphertext_bits, keystream = encrypt(original, key_hex, frame_number)
    ciphertext_hex = bits_to_hex(ciphertext_bits)
    print(f"Зашифровано (HEX): {ciphertext_hex}")

    decrypted = decrypt(ciphertext_bits, key_hex, frame_number)
    print(f"Расшифровано: {decrypted}")

    print("-" * 60)
    print(f"Совпадение: {original == decrypted}")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("ТЕСТ НА 1000+ СИМВОЛОВ")
    print("=" * 60)

    long_text = original * (1000 // len(original) + 1)
    long_text = long_text[:1000]
    print(f"Длина текста: {len(long_text)} символов")

    cipher_bits, _ = encrypt(long_text, key_hex, frame_number)
    decrypted_long = decrypt(cipher_bits, key_hex, frame_number)

    print(f"Первые 50 символов исходного текста: {long_text[:50]}...")
    print(f"Первые 50 символов расшифрованного: {decrypted_long[:50]}...")
    print(f"Совпадение: {long_text == decrypted_long}")
    print("=" * 60)
