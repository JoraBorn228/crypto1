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

    @staticmethod
    def _is_encrypted_character(char):
        """Проверяет, преобразуется ли символ текущим алфавитным правилом."""
        return char.upper() in RUSSIAN_ALPHABET or char.upper() == 'Ё' or char.isalpha()

    def _restore_format(self, template, transformed):
        """Возвращает преобразованные буквы на исходные места, сохраняя разделители."""
        result = []
        letter_index = 0
        for char in template:
            if self._is_encrypted_character(char):
                if letter_index < len(transformed):
                    result.append(transformed[letter_index])
                    letter_index += 1
            else:
                result.append(char)
        # Остаток — это символы дополнения блока.
        result.extend(transformed[letter_index:])
        return ''.join(result)

    def encrypt(self, text):
        """Шифрует буквы, оставляя пробелы и знаки на прежних местах."""
        numbers = self._text_to_numbers(text)
        if not numbers:
            return text

        # Дополняем буквенную последовательность до длины, кратной размеру матрицы.
        while len(numbers) % self.size != 0:
            numbers.append(RUSSIAN_ALPHABET.index('Ъ'))

        encrypted = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            encrypted_block = np.dot(self.matrix, block) % self.mod
            encrypted.extend(encrypted_block)

        encrypted_letters = self._numbers_to_text(encrypted)
        return self._restore_format(text, encrypted_letters)

    def decrypt(self, text, remove_padding=True):
        """Расшифровывает буквы, сохраняя пробелы и знаки на прежних местах."""
        numbers = self._text_to_numbers(text)
        if not numbers:
            return text

        # Длина буквенной последовательности должна делиться на размер матрицы.
        if len(numbers) % self.size != 0:
            while len(numbers) % self.size != 0:
                numbers.append(RUSSIAN_ALPHABET.index('Ъ'))

        decrypted = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            decrypted_block = np.dot(self.inverse_matrix, block) % self.mod
            decrypted.extend(decrypted_block)

        decrypted_letters = self._numbers_to_text(decrypted)
        if remove_padding:
            decrypted_letters = decrypted_letters.rstrip('Ъ')
        return self._restore_format(text, decrypted_letters)


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

    while True:

        print("\n" + "=" * 50)
        print("МАТРИЧНЫЙ ШИФР (Шифр Хилла)")
        print("=" * 50)
        print("1. Зашифровать")
        print("2. Расшифровать")
        print("3. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":

            text = input("Введите текст для шифрования: ")

            print("\nВведите матрицу-ключ")
            print("Пример: 3 2 1, 1 1 1, 1 2 3")

            try:

                matrix_str = input("Матрица: ").strip()

                rows = matrix_str.split(',')
                matrix = []

                for row in rows:
                    matrix.append(
                        list(map(int, row.strip().split()))
                    )

                is_valid, message = validate_matrix(matrix)

                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue

                cipher = MatrixCipher(matrix)

                encrypted = cipher.encrypt(text)

                print("\nРезультат шифрования:")
                print(encrypted)

            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":

            text = input("Введите текст для расшифрования: ")

            print("\nВведите ту же матрицу-ключ")

            try:

                matrix_str = input("Матрица: ").strip()

                rows = matrix_str.split(',')
                matrix = []

                for row in rows:
                    matrix.append(
                        list(map(int, row.strip().split()))
                    )

                is_valid, message = validate_matrix(matrix)

                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue

                cipher = MatrixCipher(matrix)

                decrypted = cipher.decrypt(text)

                print("\nРезультат расшифрования:")
                print(decrypted)

            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":

            print("Выход из программы...")
            break

        else:

            print("Неверный выбор!")


if __name__ == "__main__":
    main()