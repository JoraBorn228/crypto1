import sys

# Таблицы S-box, обратный S-box и Rcon (как в оригинале)
SBOX = [
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
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

INV_SBOX = [
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
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

def xtime(x):
    return ((x << 1) ^ (0x1b if (x & 0x80) else 0x00)) & 0xff

class AES:
    def __init__(self):
        self.Nk = 0
        self.Nr = 0
        self.w = [0] * (60 * 4)

    def set_key(self, key):
        key_len = len(key)
        self.Nk = key_len // 4
        self.Nr = {4: 10, 6: 12, 8: 14}[self.Nk]
        for i in range(self.Nk):
            self.w[4*i + 0] = key[4*i + 0]
            self.w[4*i + 1] = key[4*i + 1]
            self.w[4*i + 2] = key[4*i + 2]
            self.w[4*i + 3] = key[4*i + 3]
        for i in range(self.Nk, 4 * (self.Nr + 1)):
            temp = [self.w[4*(i-1)+0], self.w[4*(i-1)+1], self.w[4*(i-1)+2], self.w[4*(i-1)+3]]
            if i % self.Nk == 0:
                temp = [temp[1], temp[2], temp[3], temp[0]]
                temp = [SBOX[b] for b in temp]
                temp[0] ^= RCON[i // self.Nk]
            elif self.Nk > 6 and i % self.Nk == 4:
                temp = [SBOX[b] for b in temp]
            self.w[4*i + 0] = self.w[4*(i - self.Nk) + 0] ^ temp[0]
            self.w[4*i + 1] = self.w[4*(i - self.Nk) + 1] ^ temp[1]
            self.w[4*i + 2] = self.w[4*(i - self.Nk) + 2] ^ temp[2]
            self.w[4*i + 3] = self.w[4*(i - self.Nk) + 3] ^ temp[3]

    def add_round_key(self, state, rnd):
        for i in range(4):
            for j in range(4):
                state[j][i] ^= self.w[4 * (rnd * 4 + i) + j]

    def sub_bytes(self, state):
        for i in range(4):
            for j in range(4):
                state[i][j] = SBOX[state[i][j]]

    def inv_sub_bytes(self, state):
        for i in range(4):
            for j in range(4):
                state[i][j] = INV_SBOX[state[i][j]]

    def shift_rows(self, state):
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]

    def inv_shift_rows(self, state):
        state[1] = state[1][-1:] + state[1][:-1]
        state[2] = state[2][-2:] + state[2][:-2]
        state[3] = state[3][-3:] + state[3][:-3]

    def mix_columns(self, state):
        for j in range(4):
            a = state[0][j]
            b = state[1][j]
            c = state[2][j]
            d = state[3][j]
            state[0][j] = xtime(a) ^ xtime(b) ^ b ^ c ^ d
            state[1][j] = a ^ xtime(b) ^ xtime(c) ^ c ^ d
            state[2][j] = a ^ b ^ xtime(c) ^ xtime(d) ^ d
            state[3][j] = xtime(a) ^ a ^ b ^ c ^ xtime(d)

    def inv_mix_columns(self, state):
        for j in range(4):
            a = state[0][j]
            b = state[1][j]
            c = state[2][j]
            d = state[3][j]
            state[0][j] = (xtime(xtime(xtime(a) ^ xtime(c)) ^ xtime(xtime(b) ^ xtime(d))) ^
                           xtime(xtime(a ^ c) ^ xtime(b ^ d)) ^ a ^ b ^ c ^ d) & 0xff
            state[1][j] = (xtime(xtime(xtime(b) ^ xtime(d)) ^ xtime(xtime(a) ^ xtime(c))) ^
                           xtime(xtime(b ^ d) ^ xtime(a ^ c)) ^ a ^ b ^ c ^ d) & 0xff
            state[2][j] = (xtime(xtime(xtime(c) ^ xtime(a)) ^ xtime(xtime(d) ^ xtime(b))) ^
                           xtime(xtime(c ^ a) ^ xtime(d ^ b)) ^ a ^ b ^ c ^ d) & 0xff
            state[3][j] = (xtime(xtime(xtime(d) ^ xtime(b)) ^ xtime(xtime(c) ^ xtime(a))) ^
                           xtime(xtime(d ^ b) ^ xtime(c ^ a)) ^ a ^ b ^ c ^ d) & 0xff

    def encrypt_block(self, plain):
        state = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[j][i] = plain[i*4 + j]
        self.add_round_key(state, 0)
        for rnd in range(1, self.Nr):
            self.sub_bytes(state)
            self.shift_rows(state)
            self.mix_columns(state)
            self.add_round_key(state, rnd)
        self.sub_bytes(state)
        self.shift_rows(state)
        self.add_round_key(state, self.Nr)
        out = bytearray(16)
        for i in range(4):
            for j in range(4):
                out[i*4 + j] = state[j][i]
        return bytes(out)

    def decrypt_block(self, cipher):
        state = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[j][i] = cipher[i*4 + j]
        self.add_round_key(state, self.Nr)
        for rnd in range(self.Nr - 1, 0, -1):
            self.inv_shift_rows(state)
            self.inv_sub_bytes(state)
            self.add_round_key(state, rnd)
            self.inv_mix_columns(state)
        self.inv_shift_rows(state)
        self.inv_sub_bytes(state)
        self.add_round_key(state, 0)
        out = bytearray(16)
        for i in range(4):
            for j in range(4):
                out[i*4 + j] = state[j][i]
        return bytes(out)

class AESCipher:
    def __init__(self):
        self.aes = AES()
        self.key_set = False

    def set_key_from_hex(self, key_hex):
        key_hex = key_hex.strip().lower()
        if len(key_hex) not in (32, 48, 64):
            print("Ошибка: длина ключа должна быть 32, 48 или 64 hex-символа (16, 24 или 32 байта).")
            return False
        try:
            key_bytes = bytes.fromhex(key_hex)
        except ValueError:
            print("Ошибка: неверный hex-формат ключа.")
            return False
        self.aes.set_key(key_bytes)
        self.key_set = True
        bits = len(key_bytes) * 8
        print(f"Ключ установлен ({bits} бит): {key_hex.upper()}")
        return True

    def encrypt_hex(self, plain_hex):
        if not self.key_set:
            print("Ошибка: ключ не установлен!")
            return ""
        try:
            data = bytes.fromhex(plain_hex)
        except ValueError:
            print("Ошибка: неверный hex-формат открытого текста.")
            return ""
        # Требуем, чтобы длина данных была кратна 16 байтам
        if len(data) % 16 != 0:
            print("Ошибка: длина открытого текста должна быть кратна 16 байтам (32 hex-символа).")
            return ""
        cipher = bytearray()
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            enc_block = self.aes.encrypt_block(block)
            cipher.extend(enc_block)
        return cipher.hex().upper()

    def decrypt_hex(self, cipher_hex):
        if not self.key_set:
            print("Ошибка: ключ не установлен!")
            return ""
        try:
            cipher = bytes.fromhex(cipher_hex)
        except ValueError:
            print("Ошибка: неверный hex-формат зашифрованного текста.")
            return ""
        if len(cipher) % 16 != 0:
            print("Ошибка: длина зашифрованного текста должна быть кратна 16 байтам.")
            return ""
        plain = bytearray()
        for i in range(0, len(cipher), 16):
            block = cipher[i:i+16]
            dec_block = self.aes.decrypt_block(block)
            plain.extend(dec_block)
        return plain.hex().upper()

def main():
    cipher = AESCipher()
    while True:
        print("\nAES")
        print("1. Установить ключ (hex)")
        print("2. Зашифровать hex")
        print("3. Расшифровать hex")
        print("4. Выход")
        choice = input("Ваш выбор: ").strip()
        if choice == '1':
            key_hex = input("Введите ключ в hex: ").strip()
            cipher.set_key_from_hex(key_hex)
        elif choice == '2':
            plain_hex = input("Введите открытый текст в hex: ").strip()
            enc = cipher.encrypt_hex(plain_hex)
            if enc:
                print(f"Зашифрованный текст: {enc}")
        elif choice == '3':
            cipher_hex = input("Введите зашифрованный текст в hex: ").strip()
            dec = cipher.decrypt_hex(cipher_hex)
            if dec:
                print(f"Расшифрованный текст: {dec}")
        elif choice == '4':
            print("Программа завершена.")
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()
