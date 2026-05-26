import math

def is_coprime(x, y):
    return math.gcd(x, y) == 1

alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"
M = 32

def generate_gamma(length, a, c, t):
    gamma = []
    current = (a * t + c) % M
    gamma.append(current)
    for _ in range(length - 1):
        current = (a * current + c) % M
        gamma.append(current)
    return gamma

def validate_a(a):
    return a % 4 == 1 and 1 <= a < M

def validate_c(c):
    return is_coprime(c, M) and 1 <= c < M

def get_params():
    while True:
        print(f"Введите число a (a mod 4 = 1, от 1 до {M-1})")
        print("Допустимые значения: 1, 5, 9, 13, 17, 21, 25, 29")
        a = int(input())
        if validate_a(a):
            break
        print(f"Ошибка: a должно удовлетворять условию a mod 4 = 1")

    while True:
        print(f"Введите число c (взаимно простое с {M}, нечётное, от 1 до {M-1})")
        c = int(input())
        if validate_c(c):
            break
        print(f"Ошибка: c должно быть взаимно простым с {M} (нечётным)")

    print("Введите число T (начальное значение, от 0 до 31)")
    t = int(input())
    
    return a, c, t

def encrypt(text, a, c, t):
    text = text.upper()
    gamma = generate_gamma(len(text), a, c, t)
    
    encrypted_indices = []
    encrypted_text = []
    
    for i, char in enumerate(text):
        if char in alphabet:
            char_index = alphabet.index(char)
            encrypted_index = (char_index + gamma[i]) % M
            encrypted_indices.append(encrypted_index)
            encrypted_text.append(alphabet[encrypted_index])
    
    return encrypted_indices, ''.join(encrypted_text), gamma

def decrypt(encrypted_indices, a, c, t):
    gamma = generate_gamma(len(encrypted_indices), a, c, t)
    
    decrypted_indices = []
    decrypted_text = []
    
    for i, enc_index in enumerate(encrypted_indices):
        dec_index = (enc_index - gamma[i]) % M
        decrypted_indices.append(dec_index)
        decrypted_text.append(alphabet[dec_index])
    
    return ''.join(decrypted_text)

def main():
    print("=== Одноразовый блокнот К. Шеннона ===")
    print(f"Алфавит ({M} символов): {alphabet}\n")
    
    print("--- Шифрование ---")
    print("Введите текст для шифрования:")
    text = input().upper()
    
    filtered_text = ''.join(c for c in text if c in alphabet)
    print(f"Текст (только буквы алфавита): {filtered_text}")
    
    a, c, t = get_params()
    
    encrypted_indices, encrypted_text, gamma = encrypt(filtered_text, a, c, t)
    
    print(f"\nГамма: {gamma}")
    print(f"Зашифрованный текст (числа): {encrypted_indices}")
    print(f"Зашифрованный текст (буквы): {encrypted_text}")
    
    print("\n--- Расшифрование ---")
    print("Используем те же параметры a, c, T для расшифрования...")
    
    decrypted_text = decrypt(encrypted_indices, a, c, t)
    print(f"Расшифрованный текст: {decrypted_text}")
    
    if decrypted_text == filtered_text:
        print("\nПроверка пройдена: исходный текст совпадает с расшифрованным!")
    else:
        print("\nОшибка: тексты не совпадают!")

if __name__ == "__main__":
    main()
