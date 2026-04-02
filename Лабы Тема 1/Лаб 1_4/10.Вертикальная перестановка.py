# Шифр вертикальной перестановки (Вариант 10)
# Ключ - слово "МАГМА" (буквы могут повторяться)
# Пустые клетки НЕ ЗАПОЛНЯЮТСЯ

def proverka_klucha(key):
    """Проверка ключа-слова"""
    if not key.isalpha():
        print("❌ Ошибка: Ключ должен состоять только из букв!")
        return False
    
    print(f"✅ Ключ '{key}' принят!")
    return True


def poluchit_poryadok_stolbcov(key):
    """
    Получает порядок столбцов на основе алфавитного порядка букв ключа
    Для повторяющихся букв использует порядковый номер (1,2,3...)
    """
    print(f"\n🔑 Анализ ключа '{key}':")
    print("-" * 50)
    print("Исходная позиция | Буква | Номер повтора | Новый порядок")
    print("-" * 50)
    
    # Считаем сколько раз встретилась каждая буква
    letter_count = {}
    letters_with_pos = []
    
    for i, letter in enumerate(key):
        # Увеличиваем счетчик для буквы
        if letter in letter_count:
            letter_count[letter] += 1
        else:
            letter_count[letter] = 1
        
        # Запоминаем букву, позицию и номер повтора
        letters_with_pos.append((letter, i, letter_count[letter]))
    
    # Сортируем: сначала по букве, потом по номеру повтора
    # Для одинаковых букв меньший номер повтора идет первым
    sorted_letters = sorted(letters_with_pos, key=lambda x: (x[0], x[2]))
    
    # Создаем словарь: исходная позиция -> новый порядок
    order = {}
    for new_pos, (letter, old_pos, repeat_num) in enumerate(sorted_letters):
        order[old_pos] = new_pos + 1  # +1 для человеко-читаемого формата
    
    # Создаем ключ-цифру
    numeric_key = ''.join(str(order[i]) for i in range(len(key)))
    
    # Выводим таблицу анализа
    for i in range(len(key)):
        letter = key[i]
        # Находим номер повтора для этой позиции
        repeat = 1
        for j in range(i):
            if key[j] == letter:
                repeat += 1
        print(f"       {i+1}         |   {letter}   |       {repeat}       |       {order[i]}")
    
    print("-" * 50)
    print(f"👉 Ключ для шифрования: {numeric_key}")
    
    return numeric_key, sorted_letters


def shifrovat(text, word_key):
    """Шифрование вертикальной перестановкой (без заполнения пустых клеток)"""
    print("\n" + "="*70)
    print("🔐 НАЧИНАЕМ ШИФРОВАНИЕ")
    print("="*70)
    
    # Получаем числовой ключ из слова
    numeric_key, sorted_letters = poluchit_poryadok_stolbcov(word_key)
    
    # Шаг 1: Подготавливаем текст
    original_text = text
    text = text.replace(" ", "").upper()
    print(f"\n📝 Исходный текст: '{original_text}'")
    print(f"1. Текст без пробелов (upper): {text}")
    print(f"   Длина текста: {len(text)} символов")
    
    # Шаг 2: Определяем размер таблицы
    cols = len(word_key)  # количество столбцов = длина ключа
    rows = (len(text) + cols - 1) // cols  # количество строк
    
    print(f"2. Таблица будет размером {rows} строк × {cols} столбцов")
    print(f"   ⚠️ Пустые клетки останутся пустыми (не заполняются)")
    
    # Шаг 3: Записываем текст в таблицу по строкам
    print("\n3. Заполняем таблицу по строкам (пустые клетки - '.'):")
    print("-" * 70)
    
    # Печатаем заголовок с ключом
    print("   ", end="")
    for i, letter in enumerate(word_key):
        print(f"  {letter}({i+1}) ", end="")
    print("\n   " + "-" * (cols * 7))
    
    matrix = []
    index = 0
    total_chars = len(text)
    
    for i in range(rows):
        row = []
        print(f"   |", end="")
        for j in range(cols):
            if index < total_chars:
                row.append(text[index])
                print(f"  {text[index]}  |", end="")
                index += 1
            else:
                row.append('.')  # Пустая клетка
                print(f"  .  |", end="")
        matrix.append(row)
        print(f"  строка {i+1}")
        print("   " + "-" * (cols * 7))
    
    # Шаг 4: Читаем по столбцам в порядке, определенном ключом
    print("\n4. Читаем столбцы в порядке сортировки букв ключа:")
    print("   (пропуская пустые клетки)")
    
    result = ""
    print("\n   Порядок чтения столбцов:")
    for new_pos, (letter, col, repeat_num) in enumerate(sorted_letters):
        column_text = ""
        print(f"   {new_pos+1}. Столбец {col+1} (буква '{letter}' №{repeat_num}): ", end="")
        for row in range(rows):
            if matrix[row][col] != '.':  # Пропускаем пустые клетки
                result += matrix[row][col]
                column_text += matrix[row][col]
        print(column_text)
    
    print("\n" + "="*70)
    print(f"🔐 РЕЗУЛЬТАТ ШИФРОВАНИЯ: {result}")
    print("="*70)
    
    return result, numeric_key, sorted_letters, rows, cols


def rasshifrovat(cipher, word_key, numeric_key, sorted_letters, rows, cols):
    """Расшифрование вертикальной перестановки (с пустыми клетками)"""
    print("\n" + "="*70)
    print("🔓 НАЧИНАЕМ РАСШИФРОВАНИЕ")
    print("="*70)
    
    print(f"1. Таблица {rows}×{cols} (с пустыми клетками)")
    print(f"2. Шифротекст: {cipher}")
    print(f"3. Ключ-слово: {word_key}")
    print(f"4. Числовой ключ: {numeric_key}")
    
    # Создаем пустую таблицу
    matrix = [['.' for _ in range(cols)] for _ in range(rows)]
    
    # Сначала нужно определить, в каких столбцах есть пустые клетки
    # Вычисляем сколько символов в каждом столбце
    total_chars = len(cipher)
    chars_per_column = [rows] * cols  # по умолчанию во всех столбцах rows символов
    
    # В последних столбцах может быть меньше символов
    empty_in_last_row = cols * rows - total_chars
    if empty_in_last_row > 0:
        # Пустые клетки в последней строке, начиная с последних столбцов
        for i in range(empty_in_last_row):
            chars_per_column[cols - 1 - i] -= 1
    
    print(f"\n   Количество символов в каждом столбце: {chars_per_column}")
    
    # Заполняем по столбцам в порядке, определенном ключом
    index = 0
    print("\n5. Заполняем таблицу по столбцам в порядке сортировки букв:")
    
    for new_pos, (letter, col, repeat_num) in enumerate(sorted_letters):
        print(f"\n   {new_pos+1}. Столбец {col+1} (буква '{letter}' №{repeat_num}): ", end="")
        # Сколько символов нужно записать в этот столбец
        chars_in_this_col = chars_per_column[col]
        for row in range(chars_in_this_col):
            matrix[row][col] = cipher[index]
            print(f"{cipher[index]}", end="")
            index += 1
        # Остальные клетки в столбце остаются '.'
    
    # Показываем заполненную таблицу
    print("\n\n6. Заполненная таблица:")
    print("-" * 70)
    print("   ", end="")
    for i, letter in enumerate(word_key):
        print(f"  {letter}({i+1}) ", end="")
    print("\n   " + "-" * (cols * 7))
    
    for i in range(rows):
        print(f"   |", end="")
        for j in range(cols):
            print(f"  {matrix[i][j]}  |", end="")
        print(f"  строка {i+1}")
        print("   " + "-" * (cols * 7))
    
    # Читаем по строкам (пропуская пустые клетки)
    print("\n7. Читаем результат по строкам (пропуская пустые клетки):")
    result = ""
    for i in range(rows):
        row_text = ""
        for j in range(cols):
            if matrix[i][j] != '.':
                result += matrix[i][j]
                row_text += matrix[i][j]
        print(f"   Строка {i+1}: {row_text}")
    
    print(f"\n8. Результат: {result}")
    return result


# ============ ГЛАВНАЯ ПРОГРАММА ============

print("="*70)
print("🔐 ШИФР ВЕРТИКАЛЬНОЙ ПЕРЕСТАНОВКИ (Вариант 10)")
print("   Ключ - слово (буквы МОГУТ ПОВТОРЯТЬСЯ)")
print("   ⚠️ Пустые клетки НЕ ЗАПОЛНЯЮТСЯ")
print("="*70)
print()

# Ручной ввод текста
print("Введите текст для шифрования:")
text = input(">>> ")
if not text:
    text = "Леопард не может изменить своих пятен"
    print(f"Используем текст по умолчанию: '{text}'")

print(f"\nИсходный текст: {text}")
print()

# Ручной ввод ключа-слова
while True:
    print("Введите ключевое слово (например, МАГМА, КРИПТО, ПЕРЕСТАНОВКА)")
    print("Буквы МОГУТ ПОВТОРЯТЬСЯ!")
    word_key = input(">>> ").upper()
    
    if not word_key:
        word_key = "МАГМА"
        print(f"Используем ключ по умолчанию: '{word_key}'")
    
    if proverka_klucha(word_key):
        break
    print("Попробуйте ещё раз.\n")

print("\n" + "="*70)

# Шифруем
cipher, numeric_key, sorted_letters, rows, cols = shifrovat(text, word_key)

# Расшифровываем
decrypted = rasshifrovat(cipher, word_key, numeric_key, sorted_letters, rows, cols)

# Проверка
print("\n" + "="*70)
print("🔍 ПРОВЕРКА:")
print("="*70)
original_clean = text.replace(" ", "").upper()
print(f"Исходный текст (без пробелов): {original_clean}")
print(f"Расшифрованный текст:          {decrypted}")
if original_clean == decrypted:
    print("\n✅ УСПЕХ! Текст расшифрован правильно!")
else:
    print("\n❌ Ошибка при расшифровании")
print("="*70)