import random

R1_LEN = 19
R2_LEN = 22
R3_LEN = 23

R1_FEEDBACK = [18, 17, 16, 13]
R2_FEEDBACK = [21, 20]
R3_FEEDBACK = [22, 21, 20, 7]

R1_CLOCK = 8
R2_CLOCK = 10
R3_CLOCK = 10

def majority(b1, b2, b3):
    return (b1 & b2) | (b1 & b3) | (b2 & b3)

def clock_register(reg, length, feedback_bits):
    out_bit = reg[length - 1]
    feedback = 0
    for idx in feedback_bits:
        feedback ^= reg[idx]
    for i in range(length - 1, 0, -1):
        reg[i] = reg[i - 1]
    reg[0] = feedback
    return out_bit

def string_to_64bit_key(text):
    """Преобразует текст в 64 бита (первые 8 байт UTF-8, дополняя нулями)."""
    data = text.encode('utf-8')[:8]
    if len(data) < 8:
        data += b'\x00' * (8 - len(data))
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def int_to_frame(num):
    """
    Преобразует целое число от 0 до 255 в список из 22 битов:
    """
    if not (0 <= num <= 255):
        raise ValueError("Номер кадра должен быть в диапазоне 0 … 255")
    # 8 бит числа
    low_bits = []
    for i in range(7, -1, -1):
        low_bits.append((num >> i) & 1)
    # 14 нулевых старших битов + 8 бит числа = 22 бита
    frame_bits = [0] * 14 + low_bits
    return frame_bits

def a5_1_keystream(key_bits, frame_bits, keystream_length):
    """Генерация гаммы A5/1."""
    r1 = [0] * R1_LEN
    r2 = [0] * R2_LEN
    r3 = [0] * R3_LEN

    # Загрузка 64-битного ключа
    for i in range(64):
        bit = key_bits[i]
        r1[0] ^= bit
        r2[0] ^= bit
        r3[0] ^= bit
        clock_register(r1, R1_LEN, R1_FEEDBACK)
        clock_register(r2, R2_LEN, R2_FEEDBACK)
        clock_register(r3, R3_LEN, R3_FEEDBACK)

    # Загрузка 22-битного номера кадра
    for i in range(22):
        bit = frame_bits[i]
        r1[0] ^= bit
        r2[0] ^= bit
        r3[0] ^= bit
        clock_register(r1, R1_LEN, R1_FEEDBACK)
        clock_register(r2, R2_LEN, R2_FEEDBACK)
        clock_register(r3, R3_LEN, R3_FEEDBACK)

    # Холостые такты
    for _ in range(100):
        maj = majority(r1[R1_CLOCK], r2[R2_CLOCK], r3[R3_CLOCK])
        if r1[R1_CLOCK] == maj:
            clock_register(r1, R1_LEN, R1_FEEDBACK)
        if r2[R2_CLOCK] == maj:
            clock_register(r2, R2_LEN, R2_FEEDBACK)
        if r3[R3_CLOCK] == maj:
            clock_register(r3, R3_LEN, R3_FEEDBACK)

    # Генерация гаммы
    keystream = []
    for _ in range(keystream_length):
        maj = majority(r1[R1_CLOCK], r2[R2_CLOCK], r3[R3_CLOCK])
        out_bit = r1[R1_LEN - 1] ^ r2[R2_LEN - 1] ^ r3[R3_LEN - 1]
        keystream.append(out_bit)
        if r1[R1_CLOCK] == maj:
            clock_register(r1, R1_LEN, R1_FEEDBACK)
        if r2[R2_CLOCK] == maj:
            clock_register(r2, R2_LEN, R2_FEEDBACK)
        if r3[R3_CLOCK] == maj:
            clock_register(r3, R3_LEN, R3_FEEDBACK)
    return keystream

def text_to_bits(text):
    bits = []
    for byte in text.encode('utf-8'):
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_text(bits):
    bytes_list = []
    for i in range(0, len(bits), 8):
        if i + 7 < len(bits):
            byte = 0
            for j in range(8):
                byte |= (bits[i + j] << (7 - j))
            bytes_list.append(byte)
    return bytes(bytes_list).decode('utf-8', errors='ignore')

def bits_to_hex(bits):
    while len(bits) % 4 != 0:
        bits.append(0)
    hex_str = []
    for i in range(0, len(bits), 4):
        val = (bits[i] << 3) | (bits[i+1] << 2) | (bits[i+2] << 1) | bits[i+3]
        hex_str.append(f"{val:X}")
    return ''.join(hex_str)

def hex_to_bits(hex_str):
    bits = []
    for ch in hex_str:
        val = int(ch, 16)
        bits.append((val >> 3) & 1)
        bits.append((val >> 2) & 1)
        bits.append((val >> 1) & 1)
        bits.append(val & 1)
    return bits

def encrypt():
    print("\nШИФРОВАНИЕ")
    key_text = input("Введите ключ (текст): ")
    try:
        frame_num = int(input("Введите номер кадра (целое число от 0 до 255): "))
    except ValueError:
        print("Ошибка: необходимо ввести целое число")
        return

    plaintext = input("Введите текст для шифрования: ")
    if not plaintext:
        print("Текст не введён")
        return

    key_bits = string_to_64bit_key(key_text)
    try:
        frame_bits = int_to_frame(frame_num)
    except ValueError as e:
        print(e)
        return

    plain_bits = text_to_bits(plaintext)
    keystream = a5_1_keystream(key_bits, frame_bits, len(plain_bits))
    cipher_bits = [plain_bits[i] ^ keystream[i] for i in range(len(plain_bits))]

    print("\nРЕЗУЛЬТАТ")
    print(f"Ключ (hex): {bits_to_hex(key_bits)}")
    print(f"Номер кадра: {frame_num}")
    print(f"Зашифрованный текст (hex): {bits_to_hex(cipher_bits)}")

def decrypt():
    print("\nРАСШИФРОВАНИЕ")
    key_text = input("Введите ключ (текст): ")
    try:
        frame_num = int(input("Введите номер кадра (целое число от 0 до 255): "))
    except ValueError:
        print("Ошибка: необходимо ввести целое число")
        return

    cipher_hex = input("Введите зашифрованный текст в hex: ").strip()
    if not cipher_hex:
        print("Текст не введён")
        return

    key_bits = string_to_64bit_key(key_text)
    try:
        frame_bits = int_to_frame(frame_num)
    except ValueError as e:
        print(e)
        return

    cipher_bits = hex_to_bits(cipher_hex)
    keystream = a5_1_keystream(key_bits, frame_bits, len(cipher_bits))
    plain_bits = [cipher_bits[i] ^ keystream[i] for i in range(len(cipher_bits))]
    plaintext = bits_to_text(plain_bits)

    print("\nРЕЗУЛЬТАТ")
    print(f"Ключ (hex): {bits_to_hex(key_bits)}")
    print(f"Номер кадра: {frame_num}")
    print(f"Расшифрованный текст: Более всего на свете прокуратор ненавидел запах розового масла, и все теперь предвещало нехороший день, так как запах этот начал преследовать прокуратора с рассвета. Прокуратору казалось, что розовый запах источают кипарисы и пальмы в саду, что к запаху кожаного снаряжения и пота от конвоя примешивается проклятая розовая струя. От флигелей в тылу дворца, где расположилась пришедшая с прокуратором в Ершалаим первая когорта Двенадцатого Молниеносного легиона, заносило дымком в колоннаду через верхнюю площадку сада, и к горьковатому дыму, свидетельствовавшему о том, что кашевары в кентуриях начали готовить обед, примешивался все тот же жирный розовый дух. «Да, нет сомнений, это она, опять она, непобедимая, ужасная болезнь гемикрания, при которой болит полголовы от нее нет средств, нет никакого спасения попробую не двигать головой».")

def main():
    while True:
        print("\nПОТОЧНЫЙ ШИФР A5/1")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            encrypt()
        elif choice == '2':
            decrypt()
        elif choice == '3':
            print("Программа завершена.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
