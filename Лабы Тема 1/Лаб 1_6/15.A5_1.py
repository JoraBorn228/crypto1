"""
ПОТОЧНЫЙ ШИФР A5/1
Используется в GSM для шифрования голосовых данных.
Состоит из трёх LFSR (регистров сдвига с линейной обратной связью).
"""

class LFSR:
    def __init__(self, size, taps, clock_bit):
        self.size = size
        self.taps = taps
        self.clock_bit = clock_bit
        self.register = [0] * size

    def set_register(self, bits):
        for i in range(min(len(bits), self.size)):
            self.register[i] = bits[i]

    def clock(self):
        feedback = 0
        for tap in self.taps:
            feedback ^= self.register[tap]
        self.register = [feedback] + self.register[:-1]
        return self.register[-1]

    def get_clock_bit(self):
        return self.register[self.clock_bit]

    def get_output(self):
        return self.register[-1]


class A5_1:
    def __init__(self):
        self.lfsr1 = LFSR(19, [18, 17, 16, 13], 8)
        self.lfsr2 = LFSR(22, [21, 20], 10)
        self.lfsr3 = LFSR(23, [22, 21, 20, 7], 10)

    def majority(self, x, y, z):
        return (x & y) | (x & z) | (y & z)

    def clock_all(self):
        maj = self.majority(
            self.lfsr1.get_clock_bit(),
            self.lfsr2.get_clock_bit(),
            self.lfsr3.get_clock_bit()
        )
        if self.lfsr1.get_clock_bit() == maj:
            self.lfsr1.clock()
        if self.lfsr2.get_clock_bit() == maj:
            self.lfsr2.clock()
        if self.lfsr3.get_clock_bit() == maj:
            self.lfsr3.clock()

    def get_output_bit(self):
        return self.lfsr1.get_output() ^ self.lfsr2.get_output() ^ self.lfsr3.get_output()

    def initialize(self, key, frame_number):
        key_bits = []
        for byte in key:
            for i in range(8):
                key_bits.append((byte >> i) & 1)

        frame_bits = []
        for i in range(22):
            frame_bits.append((frame_number >> i) & 1)

        for i in range(64):
            if i < len(key_bits):
                bit = key_bits[i]
            else:
                bit = 0
            self.lfsr1.register = [(self.lfsr1.register[0] ^ bit)] + self.lfsr1.register[1:]
            self.lfsr2.register = [(self.lfsr2.register[0] ^ bit)] + self.lfsr2.register[1:]
            self.lfsr3.register = [(self.lfsr3.register[0] ^ bit)] + self.lfsr3.register[1:]
            self.lfsr1.clock()
            self.lfsr2.clock()
            self.lfsr3.clock()

        for i in range(22):
            bit = frame_bits[i]
            self.lfsr1.register = [(self.lfsr1.register[0] ^ bit)] + self.lfsr1.register[1:]
            self.lfsr2.register = [(self.lfsr2.register[0] ^ bit)] + self.lfsr2.register[1:]
            self.lfsr3.register = [(self.lfsr3.register[0] ^ bit)] + self.lfsr3.register[1:]
            self.lfsr1.clock()
            self.lfsr2.clock()
            self.lfsr3.clock()

        for _ in range(100):
            self.clock_all()

    def generate_keystream(self, length):
        keystream = []
        for _ in range(length):
            self.clock_all()
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

    cipher = A5_1()
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

    cipher = A5_1()
    cipher.initialize(key, frame_number)

    keystream = cipher.generate_keystream(len(ciphertext_bits))

    plaintext_bits = []
    for i in range(len(ciphertext_bits)):
        plaintext_bits.append(ciphertext_bits[i] ^ keystream[i])

    return bits_to_text(plaintext_bits)


if __name__ == "__main__":
    print("=" * 60)
    print("ПОТОЧНЫЙ ШИФР A5/1")
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
