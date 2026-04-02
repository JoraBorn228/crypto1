import math

def is_coprime(x, y):
    return math.gcd(x, y) == 1

phrase = "КРАСИВЫМИСЛОВАМИПАСТЕРНАКНЕПОМАСЛИШЬТЧК"
alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"

def shenon():
    string = input()
    m = 32
    shen = []
    a = 0
    
    # Исправленное условие: a должно быть нечётным, от 1 до 31
    while True:
        print("Введите число а (нечётное, от 1 до 31)")
        a = int(input())
        if a % 2 != 0 and 1 <= a < m:
            break
        else:
            print("Ошибка: a должно быть нечётным числом в диапазоне от 1 до 31")

    while True:
        print("Введите число c (взаимно простое с 32, от 1 до 31)")
        c = int(input())
        test = is_coprime(c, m)
        if test == True and 1 <= c < m:
            break
        else:
            print("Ошибка: число с должно быть взаимнопростым с модулем m (32) и находиться в диапазоне от 1 до 31")

    print("Введите число T (начальное значение)")
    t = int(input())

    shen.append((a*t+c) % m)

    for i in range(len(string)-1):
        temp = (a*shen[i]+c) % 32
        shen.append(temp)

    n_string = []

    for i in range(len(string)):
        b = (alphabet.find(string[i]) + shen[i]) % m
        n_string.append(b)

    print("Зашифрованный текст (числа):", n_string)
    return n_string

nn = shenon()

def shen_un(string):
    m = 32
    shen = []
    a = 0
    
    # Исправленное условие для расшифровки
    while True:
        print("Введите число а (нечётное, от 1 до 31)")
        a = int(input())
        if a % 2 != 0 and 1 <= a < m:
            break
        else:
            print("Ошибка: a должно быть нечётным числом в диапазоне от 1 до 31")

    while True:
        print("Введите число c (взаимно простое с 32, от 1 до 31)")
        c = int(input())
        test = is_coprime(c, m)
        if test == True and 1 <= c < m:
            break
        else:
            print("Ошибка: число с должно быть взаимнопростым с модулем m (32) и находиться в диапазоне от 1 до 31")

    print("Введите число T (начальное значение)")
    t = int(input())

    shen.append((a*t+c) % m)

    for i in range(len(string)-1):
        temp = (a*shen[i]+c) % 32
        shen.append(temp)

    n_string = []

    for i in range(len(string)):
        b = (string[i] - shen[i]) % m
        n_string.append(b)

    fin_string = []
    for i in range(len(n_string)):
        fin_string.append(alphabet[n_string[i]])
    
    print("Расшифрованный текст:", ''.join(fin_string))

shen_un(nn)