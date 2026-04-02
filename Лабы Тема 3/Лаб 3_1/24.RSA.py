import random
import sys

# ============================================================
# 1. ХЭШ-ФУНКЦИЯ: квадратичная функция свертки
#    по формуле: h_i = (h_{i-1} + M_i)^2 mod p
# ============================================================

def hash_square_convolution(message: str, p: int) -> int:
    """
    Вычисляет хэш сообщения по формуле:
    h0 = 0
    h_i = (h_{i-1} + code(char_i))^2 mod p
    """
    # Таблица кодов букв (русский алфавит, как в примере)
    # А=1, Б=2, ..., Я=33 (без Ё)
    russian_alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    char_to_code = {ch: i+1 for i, ch in enumerate(russian_alphabet)}
    
    h = 0
    for ch in message.upper():
        if ch in char_to_code:
            code = char_to_code[ch]
        elif ch == ' ':
            code = 0  # пробел игнорируем или можно задать отдельный код
        else:
            code = ord(ch) % p  # для латиницы / цифр
        h = (h + code) ** 2 % p
    return h


# ============================================================
# 2. ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA
# ============================================================

def gcd_extended(a, b):
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y) такие что a*x + b*y = gcd"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(e, phi):
    """Вычисляет d = e^(-1) mod phi"""
    gcd, x, _ = gcd_extended(e, phi)
    if gcd != 1:
        raise ValueError("Обратный элемент не существует")
    return x % phi


def is_prime(n, k=10):
    """Простая проверка на простоту (тест Миллера-Рабина)"""
    if n <= 3:
        return n >= 2
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=8):
    """Генерирует простое число заданной битности (для учебных целей)"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits-1) | 1  # делаем нечетным и с MSB=1
        if is_prime(n):
            return n


def generate_rsa_keys(bits=8):
    """Генерирует пару ключей RSA (public, private)"""
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:
        q = generate_prime(bits)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (обычно 65537, но для маленьких чисел берем 17)
    e = 17
    while gcd_extended(e, phi)[0] != 1:
        e += 2
    
    d = mod_inverse(e, phi)
    
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key


# ============================================================
# 3. ЦИФРОВАЯ ПОДПИСЬ RSA
# ============================================================

def sign_rsa(message: str, private_key, hash_modulus: int = 9973) -> int:
    """
    Создает цифровую подпись для сообщения.
    private_key = (d, n)
    hash_modulus - модуль для хэш-функции (должен быть меньше n)
    """
    d, n = private_key
    # 1. Вычисляем хэш сообщения
    h = hash_square_convolution(message, hash_modulus)
    # 2. Подпись = h^d mod n
    signature = pow(h, d, n)
    return signature, h


def verify_rsa(message: str, signature: int, public_key, hash_modulus: int = 9973) -> bool:
    """
    Проверяет цифровую подпись.
    public_key = (e, n)
    """
    e, n = public_key
    # 1. Вычисляем хэш сообщения
    h = hash_square_convolution(message, hash_modulus)
    # 2. Расшифровываем подпись: h' = signature^e mod n
    h_prime = pow(signature, e, n)
    # 3. Сравниваем
    return h == h_prime


# ============================================================
# 4. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================

def main():
    # Фиксированная фраза по варианту
    default_text = "Леопард не может изменить своих пятен"
    
    print("=" * 60)
    print("ЦИФРОВАЯ ПОДПИСЬ RSA С КВАДРАТИЧНЫМ ХЭШИРОВАНИЕМ")
    print("=" * 60)
    
    # Ввод текста
    text = input(f"\nВведите текст (Enter - '{default_text}'): ").strip()
    if not text:
        text = default_text
    
    print(f"\nИсходный текст: {text}")
    
    # Генерация ключей (для учебных целей используем маленькие простые числа)
    print("\n--- Генерация ключей RSA ---")
    public_key, private_key = generate_rsa_keys(bits=12)  # битность для демо
    e, n = public_key
    d, _ = private_key
    print(f"Открытый ключ: (e={e}, n={n})")
    print(f"Закрытый ключ: (d={d}, n={n})")
    
    # Модуль хэш-функции должен быть меньше n
    hash_modulus = 9973
    if hash_modulus >= n:
        hash_modulus = n - 1
    print(f"Модуль хэш-функции: {hash_modulus}")
    
    # Вычисление хэша
    h = hash_square_convolution(text, hash_modulus)
    print(f"\nХэш сообщения (квадратичная свертка): {h}")
    
    # Подпись
    signature, _ = sign_rsa(text, private_key, hash_modulus)
    print(f"\n--- ПОДПИСАНИЕ ---")
    print(f"Цифровая подпись: {signature}")
    
    # Проверка
    print(f"\n--- ПРОВЕРКА ПОДПИСИ ---")
    is_valid = verify_rsa(text, signature, public_key, hash_modulus)
    print(f"Результат проверки: {'ПОДПИСЬ ВЕРНА ✓' if is_valid else 'ПОДПИСЬ НЕВЕРНА ✗'}")
    
    # Демонстрация: изменение текста
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: проверка подписи при изменённом тексте")
    print("=" * 60)
    fake_text = text + " (фальсификация)"
    print(f"Фальсифицированный текст: {fake_text}")
    is_valid_fake = verify_rsa(fake_text, signature, public_key, hash_modulus)
    print(f"Результат проверки: {'ПОДПИСЬ ВЕРНА ✗ (ошибка!)' if is_valid_fake else 'ПОДПИСЬ НЕВЕРНА ✓'}")


if __name__ == "__main__":
    main()