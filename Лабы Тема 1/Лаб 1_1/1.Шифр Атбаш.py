"""
ШИФР АТБАШ
Русский алфавит (33 буквы с Ъ)
Первая буква алфавита заменяется последней, вторая — предпоследней и т.д.
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = len(ALPHABET)

char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}


def encrypt(text):
    text = text.upper()
    result = []

    for char in text:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            m = char_to_num[char]
            L = (N - 1 - m) % N
            result.append(num_to_char[L])
        else:
            result.append(char)

    return ''.join(result)


def decrypt(ciphertext):
    return encrypt(ciphertext)  # Атбаш симметричен


while True:
    print("\n" + "=" * 50)
    print("ШИФР АТБАШ")
    print("=" * 50)
    print("1. Зашифровать")
    print("2. Расшифровать")
    print("3. Выход")

    choice = input("\nВыберите действие: ")

    if choice == "1":
        text = input("Введите текст для шифрования: ")
        encrypted = encrypt(text)

        print("\nРезультат:")
        print(encrypted)

    elif choice == "2":
        text = input("Введите текст для расшифрования: ")
        decrypted = decrypt(text)

        print("\nРезультат:")
        print(decrypted)

    elif choice == "3":
        print("Выход из программы...")
        break

    else:
        print("Неверный выбор!")