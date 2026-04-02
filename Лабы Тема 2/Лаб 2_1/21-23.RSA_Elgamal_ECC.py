import math
import random

alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"

def prepare_text(text):
    """Подготавливает текст: переводит в верхний регистр и удаляет пробелы"""
    text = text.upper()
    prepared = ""
    for char in text:
        if char in alphabet:
            prepared += char
        elif char == 'Ё':
            prepared += 'Е'
    return prepared

def is_prime(n):  
    if n <= 1:  
        return False  
    for i in range(2, int(n**0.5) + 1):  
        if n % i == 0:  
            return False  
    return True  

def is_coprime(x, y):
    return math.gcd(x, y) == 1

def f_d(e, N):
    for i in range(N):
        if (e * i) % N == 1:
            return i
    return None

def fi(n):
    f = n
    if n % 2 == 0:
        while n % 2 == 0:
            n = n // 2
        f = f // 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            while n % i == 0:
                n = n // i
            f = f // i
            f = f * (i-1)
        i = i + 2
    if n > 1:
        f = f // n
        f = f * (n-1)
    return f

def rsa():
    """Шифрование RSA"""
    string = input("Введите сообщение: ")
    string = prepare_text(string)
    
    if len(string) == 0:
        print("Ошибка: сообщение не содержит допустимых символов")
        return None, None, None, None
    
    print(f"\nПодготовленное сообщение: {string}")
    print(f"Длина сообщения: {len(string)} символов")
    
    while True:
        P = int(input("\nВведите число P (простое): "))
        if not is_prime(P):
            print("Число должно быть простым")
            continue
        break
    
    while True:
        Q = int(input("Введите число Q (простое): "))
        if not is_prime(Q):
            print("Число должно быть простым")
            continue
        break
    
    N = P * Q
    f = fi(N)
    
    print(f"\nN = {P} × {Q} = {N}")
    print(f"φ(N) = {f}")
    
    # Проверка, что N достаточно велико для алфавита
    if N < len(alphabet):
        print(f"\nВНИМАНИЕ: N = {N} меньше размера алфавита ({len(alphabet)})")
        print("Это может привести к ошибкам при расшифровке!")
        print("Рекомендуется выбрать большие простые числа, чтобы N >= 32")
        choice = input("Продолжить? (y/n): ")
        if choice.lower() != 'y':
            return None, None, None, None
    
    while True:
        e = int(input(f"\nВведите e (1 < e < {f}, взаимнопростое с {f}): "))
        if not is_coprime(f, e):
            print(f"Число {e} не взаимнопросто с {f}, попробуйте другое")
            continue
        
        d = f_d(e, f)
        
        # Проверка, что открытый и закрытый ключи не равны
        if e == d:
            print(f"\nОШИБКА: Открытый ключ e = {e} и закрытый ключ d = {d} совпадают!")
            print("Это небезопасно и не рекомендуется в криптографии.")
            print("Пожалуйста, выберите другое значение e.\n")
            continue
        
        # Дополнительная проверка: ключи не должны быть слишком близкими
        if abs(e - d) < 10:
            print(f"\nПРЕДУПРЕЖДЕНИЕ: Ключи e={e} и d={d} слишком близки!")
            print("Рекомендуется выбирать значения, которые значительно отличаются.")
            choice = input("Продолжить? (y/n): ")
            if choice.lower() != 'y':
                continue
        
        break
    
    print(f"\nЗакрытый ключ d: {d}")
    print(f"Проверка: ({e} × {d}) mod {f} = {(e * d) % f}")
    
    # Вывод открытого и закрытого ключей
    print("\n" + "=" * 50)
    print("КЛЮЧИ RSA")
    print("=" * 50)
    print(f"ОТКРЫТЫЙ КЛЮЧ (public key): ({e}, {N})")
    print(f"  - e (открытая экспонента): {e}")
    print(f"  - N (модуль): {N}")
    print(f"\nЗАКРЫТЫЙ КЛЮЧ (private key): ({d}, {N})")
    print(f"  - d (закрытая экспонента): {d}")
    print(f"  - N (модуль): {N}")
    
    if e != d:
        print(f"\n✓ Ключи различны (e ≠ d)")
    else:
        print(f"\n✗ ВНИМАНИЕ: Ключи совпадают!")
    
    print("=" * 50)
    
    encrypted_nums = []
    print(f"\nПроцесс шифрования:")
    for i in range(len(string)):
        ind = alphabet.index(string[i])
        temp = pow(ind, e, N)
        encrypted_nums.append(temp)
        print(f"  {string[i]} (индекс {ind}) -> {ind}^{e} mod {N} = {temp}")
    
    print(f"\nЗашифрованное сообщение (числа): {encrypted_nums}")
    return encrypted_nums, N, d, (e, N)

def rsaun(encrypted_nums, N, d):
    """Расшифровка RSA"""
    print(f"\nРасшифровка с параметрами: N={N}, d={d}")
    
    decrypted_nums = []
    print(f"\nПроцесс расшифровки:")
    for i in range(len(encrypted_nums)):
        temp = pow(encrypted_nums[i], d, N)
        decrypted_nums.append(temp)
        print(f"  {encrypted_nums[i]}^{d} mod {N} = {temp}")
    
    decrypted_text = []
    for i in decrypted_nums:
        if 0 <= i < len(alphabet):
            decrypted_text.append(alphabet[i])
        else:
            decrypted_text.append('?')
            print(f"Предупреждение: индекс {i} вне диапазона алфавита (0-{len(alphabet)-1})")
    
    return ''.join(decrypted_text), decrypted_nums

# Функции El Gamal и ECC
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def modular_inverse(a, p):
    gcd, x, _ = extended_gcd(a, p)
    if gcd != 1:
        raise ValueError(f"Обратного значения для {a} не существует по модулю {p}")
    else:
        return x % p

def solve_congruence(a, b, p):
    a_inv = modular_inverse(a, p)
    x = (a_inv * b) % p
    return x

def get_k(P, l):
    r = fi(P)
    count = 0
    ks = []
    while count != l:
        t = random.randint(1, r)
        if is_coprime(r, t):
            count += 1
            ks.append(t)
    return ks

def get_x(y, g, P):
    """Находит дискретный логарифм (только для малых P)"""
    for i in range(P):
        if pow(g, i, P) == y:
            return i
    return None

def el_gamal():
    """Шифрование El Gamal"""
    string = input("Введите сообщение: ")
    string = prepare_text(string)
    
    if len(string) == 0:
        print("Ошибка: сообщение не содержит допустимых символов")
        return None, None, None, None
    
    print(f"\nПодготовленное сообщение: {string}")
    print(f"Длина сообщения: {len(string)} символов")
    
    while True:
        P = int(input("\nВведите число P (простое): "))
        if not is_prime(P):
            print("Число должно быть простым")
            continue
        if P < len(alphabet):
            print(f"ВНИМАНИЕ: P = {P} меньше размера алфавита ({len(alphabet)})")
            print("Это может привести к ошибкам при расшифровке!")
            choice = input("Продолжить? (y/n): ")
            if choice.lower() != 'y':
                continue
        break

    while True:
        x = int(input("Введите число x (секретный ключ, 1 < x < P): "))
        if 1 < x < P:
            break
        else:
            print(f"x должно быть в диапазоне 1 < x < {P}")

    while True:
        g = int(input("Введите число g (генератор, 1 < g < P): "))
        if 1 < g < P:
            break
        else:
            print(f"g должно быть в диапазоне 1 < g < {P}")
 
    y = pow(g, x, P)
    
    # Вывод ключей El Gamal
    print("\n" + "=" * 50)
    print("КЛЮЧИ EL GAMAL")
    print("=" * 50)
    print(f"ОТКРЫТЫЙ КЛЮЧ (public key): (P={P}, g={g}, y={y})")
    print(f"  - P (простое число): {P}")
    print(f"  - g (генератор): {g}")
    print(f"  - y (открытый ключ): {y}")
    print(f"\nЗАКРЫТЫЙ КЛЮЧ (private key): x={x}")
    print("=" * 50)

    k = get_k(P, len(string))
    print(f"\nРандомизаторы k: {k}")
    
    encrypted_pairs = []
    print(f"\nПроцесс шифрования:")
    for i in range(len(string)):
        ind = alphabet.index(string[i])
        a = pow(g, k[i], P)
        b = (pow(y, k[i], P) * ind) % P
        encrypted_pairs.append([a, b])
        print(f"  {string[i]} (индекс {ind}) -> a={g}^{k[i]} mod {P}={a}, b={y}^{k[i]}*{ind} mod {P}={b}")
    
    print(f"\nЗашифрованное сообщение (пары [a,b]): {encrypted_pairs}")
    return encrypted_pairs, P, g, y

def el_gamalun(encrypted_pairs, P, g, y):
    """Расшифровка El Gamal"""
    print(f"\nРасшифровка с параметрами: P={P}, g={g}, y={y}")
    
    # Находим секретный ключ x
    x = get_x(y, g, P)
    if x is None:
        print("Ошибка: не удалось найти секретный ключ x")
        return None, None
    
    print(f"Найден секретный ключ x: {x}")
    
    decrypted_nums = []
    print(f"\nПроцесс расшифровки:")
    for i in range(len(encrypted_pairs)):
        a = encrypted_pairs[i][0]
        b = encrypted_pairs[i][1]
        a_pow = pow(a, x, P)
        a_inv = modular_inverse(a_pow, P)
        l = (b * a_inv) % P
        decrypted_nums.append(l)
        print(f"  a={a}, b={b} -> a^{x}={a_pow}, a_inv={a_inv}, l={l}")
    
    decrypted_text = []
    for i in decrypted_nums:
        if 0 <= i < len(alphabet):
            decrypted_text.append(alphabet[i])
        else:
            decrypted_text.append('?')
            print(f"Предупреждение: индекс {i} вне диапазона алфавита")
    
    return ''.join(decrypted_text), decrypted_nums

def ecc():
    """ECC шифрование (заглушка)"""
    print("\nECC шифрование пока не реализовано")
    print("Эта функция будет добавлена позже")
    return None

# Главная программа
print("=" * 50)
print("КРИПТОГРАФИЧЕСКИЕ АЛГОРИТМЫ")
print("=" * 50)
print("Выберите шифр:")
print("1. RSA")
print("2. El Gamal")
print("3. ECC")
print("=" * 50)

ch = int(input("Ваш выбор: "))

if ch == 1:
    print("\n" + "=" * 50)
    print("RSA ШИФРОВАНИЕ")
    print("=" * 50)
    
    result = rsa()
    if result[0] is not None:
        encrypted, N, d, public_key = result
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ RSA")
        print("=" * 50)
        print(f"ОТКРЫТЫЙ КЛЮЧ: {public_key}")
        print(f"ЗАКРЫТЫЙ КЛЮЧ: ({d}, {N})")
        print(f"Зашифрованное сообщение (числа): {encrypted}")
        print("=" * 50)
        
        decrypted_text, decrypted_nums = rsaun(encrypted, N, d)
        
        print("\n" + "=" * 50)
        print("РАСШИФРОВКА RSA")
        print("=" * 50)
        print(f"Расшифрованные числа: {decrypted_nums}")
        print(f"Расшифрованное сообщение: {decrypted_text}")
        print("=" * 50)

elif ch == 2:
    print("\n" + "=" * 50)
    print("EL GAMAL ШИФРОВАНИЕ")
    print("=" * 50)
    
    result = el_gamal()
    if result[0] is not None:
        encrypted, P, g, y = result
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ EL GAMAL")
        print("=" * 50)
        print(f"Зашифрованное сообщение (пары [a,b]): {encrypted}")
        print(f"Параметры для расшифровки:")
        print(f"  P = {P}")
        print(f"  g = {g}")
        print(f"  y = {y}")
        print("=" * 50)
        
        decrypted_text, decrypted_nums = el_gamalun(encrypted, P, g, y)
        
        if decrypted_text is not None:
            print("\n" + "=" * 50)
            print("РАСШИФРОВКА EL GAMAL")
            print("=" * 50)
            print(f"Расшифрованные числа: {decrypted_nums}")
            print(f"Расшифрованное сообщение: {decrypted_text}")
            print("=" * 50)

elif ch == 3:
    ecc()

else:
    print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")