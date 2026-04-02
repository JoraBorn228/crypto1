import random

alf = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н',
       'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
# phr = list('каждая кладка должна стоять на собственном днище тчк'.lower().replace(' ', ''))


def mirror(key):
    k = [[0, 0] for i in range(len(key))]
    t = 0
    for i, j in key:
        k[t] = [i, 9-j]
        t += 1
    for i in range(len(k)):
        for j in range(len(k)-1):
            if k[j][0] == k[j+1][0] and k[j][1] > k[j+1][1]:
                t = k[j][1]
                k[j][1] = k[j+1][1]
                k[j+1][1] = t
    return(k)


def rotate_180(key):
    k = [[0,0] for i in range(len(key))]
    t=0
    for i,j in key:
        k[t] = [5-i,j]
        t+=1
    k = sorted(k)
    return k


def kardano_crypt(phr):
    k_key = [(0,0), (0,3), (0,4), (0,7), (1,8), (2,2), (2,6), (3,0), (3,4),
    (3,8), (4,2), (4,3), (4,5), (4,9), (5,8)]
    crypt=[[0]*10 for i in range(6)]
    t=0
    for i,j in k_key:
        crypt[i][j] = phr[t]
        t+=1
    k_key = mirror(k_key)
    for i,j in k_key:
        try:
            crypt[i][j] = phr[t]
            t+=1
        except:
            crypt[i][j] = random.choice(alf)
    k_key = rotate_180(k_key)
    for i, j in k_key:
        try:
            crypt[i][j] = phr[t]
            t += 1
        except:
            crypt[i][j] = random.choice(alf)
    k_key = mirror(k_key)
    for i, j in k_key:
        try:
            crypt[i][j] = phr[t]
            t += 1
        except:
            crypt[i][j] = random.choice(alf)
    for i in range(len(crypt)):
        for j in range(len(crypt[i])):
            if crypt[i][j]==0:
                crypt[i][j]= random.choice(alf)
    return crypt


def kardano_decrypt(crypt):
    k_key = [(0,0), (0,3), (0,4), (0,7), (1,8), (2,2), (2,6), (3,0), (3,4),
    (3,8), (4,2), (4,3), (4,5), (4,9), (5,8)]
    decrypt = []
    for i, j in k_key:
        decrypt.append(crypt[i][j])
    k_key = mirror(k_key)
    for i, j in k_key:
        try:
            decrypt.append(crypt[i][j])
        except:
            print('s')
    k_key = rotate_180(k_key)
    for i, j in k_key:
        try:
            decrypt.append(crypt[i][j])
        except:
            print('s')
    k_key = mirror(k_key)
    for i, j in k_key:
        try:
            decrypt.append(crypt[i][j])
        except:
            print('s')
    return decrypt

def kardano_crypt_long(phr):
    """Шифрование текста любой длины"""
    result = []
    # Разбиваем на блоки по 60 символов
    for i in range(0, len(phr), 60):
        block = phr[i:i+60]
        # Если блок меньше 60, дополняем случайными буквами
        if len(block) < 60:
            block = list(block) + [random.choice(alf) for _ in range(60 - len(block))]
        # Получаем матрицу 6x10
        matrix = kardano_crypt(block)
        # Преобразуем матрицу в список символов
        for row in matrix:
            result.extend(row)
    return result

def kardano_decrypt_long(crypt_text):
    """Расшифрование текста любой длины"""
    result = []
    # Разбиваем на блоки по 60 символов
    for i in range(0, len(crypt_text), 60):
        block = crypt_text[i:i+60]
        # Создаем матрицу 6x10 из блока
        matrix = []
        for j in range(0, 60, 10):
            matrix.append(block[j:j+10])
        result.extend(kardano_decrypt(matrix))
    return result

phrase = 'Магма'
s = kardano_crypt(phrase)
t = []
for i in s:
    for j in i:
        t.append(j)
    print(i)
print('Зашифрованное: ',''.join(t))
print('Расшифрованное: ',''.join(kardano_decrypt(s)))