# МАТРИЧНЫЙ ШИФР (Шифр Хилла)
# Вариант 8: Матрица-ключ не меньше 3×3

import numpy as np
import math

# Русский алфавит (32 буквы, без Ё)
RUSSIAN_ALPHABET = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ALPHABET_SIZE = 32


class MatrixCipher:
    """Матричный шифр (шифр Хилла)"""
    
    def __init__(self, matrix):
        self.matrix = np.array(matrix, dtype=int)
        self.size = len(matrix)
        self.mod = ALPHABET_SIZE
        self.inverse_matrix = self._mod_inverse_matrix()
    
    def _mod_inverse(self, a, m):
        """Находит обратное число по модулю"""
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None
    
    def _mod_inverse_matrix(self):
        """Находит обратную матрицу по модулю"""
        det = int(round(np.linalg.det(self.matrix)))
        det_mod = det % self.mod
        
        # Проверяем, что определитель обратим по модулю
        det_inv = self._mod_inverse(det_mod, self.mod)
        if det_inv is None:
            raise ValueError(f"Матрица необратима по модулю {self.mod}")
        
        # Для матрицы 3x3 вычисляем присоединенную матрицу
        if self.size == 3:
            adjugate = self._adjugate_3x3(self.matrix)
        else:
            adjugate = np.round(det * np.linalg.inv(self.matrix)).astype(int)
        
        # Умножаем на обратный определитель по модулю
        inverse = (det_inv * adjugate) % self.mod
        return inverse.astype(int)
    
    def _adjugate_3x3(self, matrix):
        """Вычисляет присоединенную матрицу для 3x3"""
        m = matrix
        adj = np.zeros((3, 3), dtype=int)
        
        # Формулы для присоединенной матрицы 3x3
        adj[0][0] = (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        adj[1][0] = -(m[1][0] * m[2][2] - m[1][2] * m[2][0])
        adj[2][0] = (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        
        adj[0][1] = -(m[0][1] * m[2][2] - m[0][2] * m[2][1])
        adj[1][1] = (m[0][0] * m[2][2] - m[0][2] * m[2][0])
        adj[2][1] = -(m[0][0] * m[2][1] - m[0][1] * m[2][0])
        
        adj[0][2] = (m[0][1] * m[1][2] - m[0][2] * m[1][1])
        adj[1][2] = -(m[0][0] * m[1][2] - m[0][2] * m[1][0])
        adj[2][2] = (m[0][0] * m[1][1] - m[0][1] * m[1][0])
        
        return adj
    
    def _text_to_numbers(self, text):
        """Преобразует текст в числа (А=0, Б=1, ...)"""
        text = text.upper()
        numbers = []
        for char in text:
            if char in RUSSIAN_ALPHABET:
                numbers.append(RUSSIAN_ALPHABET.index(char))
            elif char == 'Ё':
                numbers.append(RUSSIAN_ALPHABET.index('Е'))
            elif char.isalpha():
                # Для английских букв
                numbers.append(ord(char) % self.mod)
        return numbers
    
    def _numbers_to_text(self, numbers):
        """Преобразует числа обратно в текст"""
        text = ''
        for num in numbers:
            text += RUSSIAN_ALPHABET[num % self.mod]
        return text
    
    def encrypt(self, text):
        """Шифрование текста"""
        # Преобразуем текст в числа
        numbers = self._text_to_numbers(text)
        
        if not numbers:
            return ""
        
        # Дополняем до длины, кратной размеру матрицы
        while len(numbers) % self.size != 0:
            numbers.append(RUSSIAN_ALPHABET.index('Ъ'))
        
        # Шифруем по блокам
        encrypted = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            encrypted_block = np.dot(self.matrix, block) % self.mod
            encrypted.extend(encrypted_block)
        
        return self._numbers_to_text(encrypted)
    
    def decrypt(self, text, remove_padding=True):
        """Расшифрование текста"""
        # Преобразуем текст в числа
        numbers = self._text_to_numbers(text)
        
        if not numbers:
            return ""
        
        # Проверяем длину
        if len(numbers) % self.size != 0:
            while len(numbers) % self.size != 0:
                numbers.append(RUSSIAN_ALPHABET.index('Ъ'))
        
        # Расшифровываем по блокам
        decrypted = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            decrypted_block = np.dot(self.inverse_matrix, block) % self.mod
            decrypted.extend(decrypted_block)
        
        result = self._numbers_to_text(decrypted)
        
        # Убираем дополнение
        if remove_padding:
            result = result.rstrip('Ъ')
        
        return result


def validate_matrix(matrix):
    """Проверяет, что матрица подходит для шифрования"""
    try:
        matrix = np.array(matrix)
        det = int(round(np.linalg.det(matrix)))
        
        # Определитель не должен быть равен 0
        if det == 0:
            return False, f"Определитель матрицы = 0 (матрица необратима)"
        
        # Определитель должен быть взаимно прост с размером алфавита
        det_mod = det % ALPHABET_SIZE
        if math.gcd(det_mod, ALPHABET_SIZE) != 1:
            return False, f"Определитель матрицы ({det}) не взаимно прост с {ALPHABET_SIZE}"
        
        return True, f"Матрица валидна (определитель = {det})"
    except Exception as e:
        return False, f"Ошибка при проверке матрицы: {e}"


def print_matrix(matrix):
    """Красиво выводит матрицу"""
    print("\nМатрица-ключ:")
    for row in matrix:
        print("  " + " ".join(f"{x:3}" for x in row))


def main():
    print("="*60)
    print("МАТРИЧНЫЙ ШИФР (Шифр Хилла)")
    print("Вариант 8: Матрица-ключ не меньше 3×3")
    print(f"Алфавит: {ALPHABET_SIZE} букв (А-Я, без Ё)")
    print("="*60)
    
    while True:
        print("\nМЕНЮ:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Работа с файлом")
        print("0. Выход")
        
        choice = input("Выберите пункт: ").strip()
        
        if choice == '0':
            print("Программа завершена.")
            break
        
        elif choice == '1':
            print("\n--- ШИФРОВАНИЕ ---")
            
            # Ввод текста
            text = input("Введите текст для шифрования: ").strip()
            if not text:
                print("Текст не введен!")
                continue
            
            # Ввод матрицы
            print("\nВведите матрицу-ключ (n×n, n ≥ 3)")
            print("Формат: строки через запятую, числа через пробел")
            print("Пример: 1 2 3, 4 5 6, 7 8 9")
            
            try:
                matrix_str = input("Матрица: ").strip()
                rows = matrix_str.split(',')
                matrix = []
                for row in rows:
                    numbers = list(map(int, row.strip().split()))
                    matrix.append(numbers)
                
                # Проверка размера
                n = len(matrix)
                if n < 3:
                    print("Ошибка: Размер матрицы должен быть не менее 3×3")
                    continue
                
                for row in matrix:
                    if len(row) != n:
                        print("Ошибка: Матрица должна быть квадратной")
                        continue
                
                # Проверка валидности
                is_valid, message = validate_matrix(matrix)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"\n✓ {message}")
                print_matrix(matrix)
                
                # Шифрование
                cipher = MatrixCipher(matrix)
                encrypted = cipher.encrypt(text)
                
                print(f"\nИсходный текст: {text}")
                print(f"Зашифрованный:  {encrypted}")
                
                # Сохранение
                save = input("\nСохранить результат? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Имя файла: ").strip()
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(encrypted)
                    print(f"Сохранено в {filename}")
                
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif choice == '2':
            print("\n--- РАСШИФРОВАНИЕ ---")
            
            # Ввод текста
            text = input("Введите текст для расшифрования: ").strip()
            if not text:
                print("Текст не введен!")
                continue
            
            # Ввод матрицы
            print("\nВведите матрицу-ключ (ту же, что при шифровании)")
            print("Формат: строки через запятую, числа через пробел")
            
            try:
                matrix_str = input("Матрица: ").strip()
                rows = matrix_str.split(',')
                matrix = []
                for row in rows:
                    numbers = list(map(int, row.strip().split()))
                    matrix.append(numbers)
                
                # Проверка размера
                n = len(matrix)
                if n < 3:
                    print("Ошибка: Размер матрицы должен быть не менее 3×3")
                    continue
                
                for row in matrix:
                    if len(row) != n:
                        print("Ошибка: Матрица должна быть квадратной")
                        continue
                
                # Проверка валидности
                is_valid, message = validate_matrix(matrix)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"\n✓ {message}")
                print_matrix(matrix)
                
                # Расшифрование
                cipher = MatrixCipher(matrix)
                decrypted = cipher.decrypt(text)
                
                print(f"\nЗашифрованный текст: {text}")
                print(f"Расшифрованный:      {decrypted}")
                
                # Сохранение
                save = input("\nСохранить результат? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Имя файла: ").strip()
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(decrypted)
                    print(f"Сохранено в {filename}")
                
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif choice == '3':
            print("\n--- РАБОТА С ФАЙЛОМ ---")
            
            filename = input("Введите имя файла: ").strip()
            if not filename:
                print("Имя файла не введено!")
                continue
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"Прочитано {len(text)} символов из файла")
                print(f"Пример: {text[:100]}...")
                
                # Ввод матрицы
                print("\nВведите матрицу-ключ:")
                matrix_str = input("Матрица: ").strip()
                rows = matrix_str.split(',')
                matrix = []
                for row in rows:
                    numbers = list(map(int, row.strip().split()))
                    matrix.append(numbers)
                
                # Проверка
                n = len(matrix)
                if n < 3:
                    print("Ошибка: Размер матрицы должен быть не менее 3×3")
                    continue
                
                is_valid, message = validate_matrix(matrix)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"\n✓ {message}")
                
                # Шифрование
                cipher = MatrixCipher(matrix)
                encrypted = cipher.encrypt(text)
                
                # Сохранение результатов
                enc_filename = f"encrypted_{filename}"
                with open(enc_filename, 'w', encoding='utf-8') as f:
                    f.write(encrypted)
                print(f"\nЗашифровано в файл: {enc_filename}")
                
                # Расшифрование для проверки
                decrypted = cipher.decrypt(encrypted)
                
                # Сравнение
                text_clean = text.upper().replace('Ё', 'Е')
                decrypted_clean = decrypted.rstrip('Ъ')
                
                if text_clean == decrypted_clean:
                    print("✓ Расшифровка успешна!")
                else:
                    print("✗ Ошибка расшифровки")
                
            except FileNotFoundError:
                print(f"Файл {filename} не найден")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        else:
            print("Неверный выбор. Попробуйте 0-3.")


if __name__ == "__main__":
    main()