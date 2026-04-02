import numpy as np
import math
import os

# Русский алфавит (32 буквы, без Ё)
RUSSIAN_ALPHABET = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ALPHABET_SIZE = 32

# Для шифра Плэйфера используем 30 букв (без Ё, Й, Ъ)
PLAYFAIR_ALPHABET = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ'


class PlayfairCipher:
    """
    Шифр Плэйфера для русского алфавита (30 букв, матрица 5x6)
    Используется Ь как разделитель, настоящие Ь не удаляются
    """
    
    def __init__(self, key):
        self.key = key.upper()
        self.rows = 5
        self.cols = 6
        self.matrix = self._create_matrix(self._prepare_key(key))
        self.padding_positions = []  # Запоминаем позиции вставленных разделителей
    
    def _prepare_key(self, key):
        key = key.upper()
        key = key.replace('Ё', 'Е')
        key = key.replace('Й', 'И')
        key = key.replace('Ъ', 'Ь')
        
        clean_key = []
        for char in key:
            if char in PLAYFAIR_ALPHABET and char not in clean_key:
                clean_key.append(char)
        
        return ''.join(clean_key)
    
    def _create_matrix(self, key):
        matrix_chars = list(key)
        for char in PLAYFAIR_ALPHABET:
            if char not in matrix_chars:
                matrix_chars.append(char)
        
        matrix = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(matrix_chars[i * self.cols + j])
            matrix.append(row)
        
        return matrix
    
    def _find_position(self, char):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.matrix[i][j] == char:
                    return i, j
        return None
    
    def _clean_text(self, text):
        text = text.upper()
        text = text.replace('Ё', 'Е')
        text = text.replace('Й', 'И')
        text = text.replace('Ъ', 'Ь')
        
        cleaned = []
        for char in text:
            if char in PLAYFAIR_ALPHABET:
                cleaned.append(char)
        
        return ''.join(cleaned)
    
    def _prepare_bigrams(self, text):
        """
        Подготовка биграмм с запоминанием позиций вставленных разделителей
        """
        original_text = text
        text = self._clean_text(text)
        
        if not text:
            return []
        
        self.padding_positions = []  # Сбрасываем позиции
        result = []
        i = 0
        original_index = 0
        
        while i < len(text):
            a = text[i]
            
            if i + 1 >= len(text):
                # Добавляем разделитель в конце
                result.append(a + 'Ь')
                self.padding_positions.append(len(result) - 1)  # Запоминаем позицию
                break
            
            b = text[i + 1]
            
            if a == b:
                # Вставляем разделитель между одинаковыми буквами
                result.append(a + 'Ь')
                self.padding_positions.append(len(result) - 1)  # Запоминаем позицию
                i += 1
            else:
                result.append(a + b)
                i += 2
            
            original_index += 2
        
        return result
    
    def _encrypt_bigram(self, bigram):
        a, b = bigram[0], bigram[1]
        
        pos_a = self._find_position(a)
        pos_b = self._find_position(b)
        
        if pos_a is None or pos_b is None:
            raise ValueError(f"Не удалось найти позицию буквы")
        
        row_a, col_a = pos_a
        row_b, col_b = pos_b
        
        if row_a == row_b:
            new_col_a = (col_a + 1) % self.cols
            new_col_b = (col_b + 1) % self.cols
            return self.matrix[row_a][new_col_a] + self.matrix[row_b][new_col_b]
        
        elif col_a == col_b:
            new_row_a = (row_a + 1) % self.rows
            new_row_b = (row_b + 1) % self.rows
            return self.matrix[new_row_a][col_a] + self.matrix[new_row_b][col_b]
        
        else:
            return self.matrix[row_a][col_b] + self.matrix[row_b][col_a]
    
    def _decrypt_bigram(self, bigram):
        a, b = bigram[0], bigram[1]
        
        pos_a = self._find_position(a)
        pos_b = self._find_position(b)
        
        if pos_a is None or pos_b is None:
            raise ValueError(f"Не удалось найти позицию буквы")
        
        row_a, col_a = pos_a
        row_b, col_b = pos_b
        
        if row_a == row_b:
            new_col_a = (col_a - 1) % self.cols
            new_col_b = (col_b - 1) % self.cols
            return self.matrix[row_a][new_col_a] + self.matrix[row_b][new_col_b]
        
        elif col_a == col_b:
            new_row_a = (row_a - 1) % self.rows
            new_row_b = (row_b - 1) % self.rows
            return self.matrix[new_row_a][col_a] + self.matrix[new_row_b][col_b]
        
        else:
            return self.matrix[row_a][col_b] + self.matrix[row_b][col_a]
    
    def encrypt(self, text):
        """Шифрование с запоминанием позиций разделителей"""
        bigrams = self._prepare_bigrams(text)
        
        encrypted = []
        for bigram in bigrams:
            encrypted.append(self._encrypt_bigram(bigram))
        
        return ''.join(encrypted)
    
    def decrypt(self, text):
        """
        Расшифрование с удалением ТОЛЬКО вставленных разделителей
        """
        text = self._clean_text(text)
        
        if len(text) % 2 != 0:
            text += 'Ь'
        
        # Расшифровываем все биграммы
        decrypted_bigrams = []
        for i in range(0, len(text), 2):
            bigram = text[i:i+2]
            decrypted_bigrams.append(self._decrypt_bigram(bigram))
        
        # Объединяем в строку
        result = ''.join(decrypted_bigrams)
        
        # Удаляем ТОЛЬКО те разделители, которые были вставлены при шифровании
        # Для этого используем сохраненные позиции
        if hasattr(self, 'padding_positions') and self.padding_positions:
            # Преобразуем строку в список для удобства удаления
            result_list = list(result)
            # Удаляем символы с сохраненных позиций (идущие с конца, чтобы не сбивать индексы)
            for pos in sorted(self.padding_positions, reverse=True):
                if pos < len(result_list) and result_list[pos] == 'Ь':
                    result_list.pop(pos)
            result = ''.join(result_list)
        
        return result
    


def validate_playfair_key(key):
    key = key.upper()
    
    key = key.replace('Ё', 'Е')
    key = key.replace('Й', 'И')
    key = key.replace('Ъ', 'Ь')
    
    for char in key:
        if char.isalpha() and char not in PLAYFAIR_ALPHABET:
            return False, f"Ключ содержит недопустимый символ: {char}"
    
    seen = set()
    duplicates = []
    for char in key:
        if char in seen:
            duplicates.append(char)
        seen.add(char)
    
    if duplicates:
        return False, f"Ключ содержит повторяющиеся буквы: {', '.join(set(duplicates))}"
    
    return True, "Ключ валиден"


def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def save_to_file(filename, text):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Результат сохранен в файл {filename}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return False


def print_sample(text, sample_size=100):
    if len(text) > sample_size:
        return text[:sample_size] + "..."
    return text


def process_file_with_cipher(filename, cipher_choice, key_params):
    text = read_file(filename)
    if text is None:
        return None, None
    
    print(f"\nПрочитано {len(text)} символов из файла {filename}")
    print(f"Пример текста: {print_sample(text)}")
    
    try:    
        if cipher_choice == '1':
            key = key_params
            cipher = PlayfairCipher(key)
            cipher.print_matrix()
            
            encrypted = cipher.encrypt(text)
            decrypted = cipher.decrypt(encrypted)
            
            return encrypted, decrypted
            
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        return None, None


def main():
    print("Инициализация программы...")
    print(f"Шифр Плэйфера: алфавит {len(PLAYFAIR_ALPHABET)} букв (без Ё, Й, Ъ)")
    
    while True:
        print("\n" + "="*70)
        print("ПРОГРАММА ШИФРОВАНИЯ")
        print("="*70)
        print("1. Шифрование")
        print("2. Расшифрование")
        print("3. Работа с файлом kolobok.txt")
        print("0. Выход")
        
        choice = input("Выберите пункт меню: ").strip()
        
        if choice == '0':
            print("Программа завершена.")
            break
        
        elif choice == '1':
            print("\n--- РЕЖИМ ШИФРОВАНИЯ ---")
            
            text = input("Введите открытый текст для шифрования: ").strip()
            if not text:
                print("Текст не введен")
                continue
            
            print(f"\nВыберите шифр для шифрования:")
            print("1. Шифр Плэйфера")
            
            cipher_choice = input("Ваш выбор 1: ").strip()   
            if cipher_choice == '1':
                print("\n--- ШИФР ПЛЭЙФЕРА ---")
                print("Алфавит: 30 букв (без Ё, Й, Ъ)")
                print("Замены: Ё→Е, Й→И, Ъ→Ь")
                
                key = input("Введите ключ: ").strip()
                
                is_valid, message = validate_playfair_key(key)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"✓ {message}")
                
                cipher = PlayfairCipher(key)
                
                result = cipher.encrypt(text)
                
                print(f"\nИсходный текст: {text}")
                print(f"Зашифрованный текст: {result}")
                
                save = input("\nСохранить результат? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Имя файла для сохранения: ").strip()
                    save_to_file(filename, result)
            
            else:
                print("Неверный выбор шифра")
        
        elif choice == '2':
            print("\n--- РЕЖИМ РАСШИФРОВАНИЯ ---")
            
            text = input("Введите зашифрованный текст для расшифрования: ").strip()
            if not text:
                print("Текст не введен")
                continue
            
            text = ''.join(text.split())
            
            print(f"\nВыберите шифр для расшифрования:")
            print("1. Шифр Плэйфера")
            
            cipher_choice = input("Ваш выбор 1: ").strip()
            
        
            
            if cipher_choice == '1':
                print("\n--- ШИФР ПЛЭЙФЕРА ---")
                print("Введите ключ, который использовался при шифровании")
                
                key = input("Введите ключ: ").strip()
                
                is_valid, message = validate_playfair_key(key)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"✓ {message}")
                
                cipher = PlayfairCipher(key)
                
                result = cipher.decrypt(text)
                
                print(f"\nЗашифрованный текст: {text}")
                print(f"Расшифрованный текст: {result}")
                
                save = input("\nСохранить результат? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Имя файла для сохранения: ").strip()
                    save_to_file(filename, result)
            
            else:
                print("Неверный выбор шифра")
        
        elif choice == '3':
            print("\n--- РАБОТА С ФАЙЛОМ kolobok.txt ---")
            
            print("Выберите шифр:")
            print("1. Шифр Плэйфера")
            
            cipher_choice = input("Ваш выбор 1: ").strip()
            
            key_params = None
            
            
            if cipher_choice == '1':
                print("\n--- ШИФР ПЛЭЙФЕРА ---")
                print("Алфавит: 30 букв (без Ё, Й, Ъ)")
                print("Замены: Ё→Е, Й→И, Ъ→Ь")
                
                key = input("Введите ключ: ").strip()
                
                is_valid, message = validate_playfair_key(key)
                if not is_valid:
                    print(f"Ошибка: {message}")
                    continue
                
                print(f"✓ {message}")
                key_params = key
                
            else:
                print("Неверный выбор шифра")
                continue
            
            encrypted, decrypted = process_file_with_cipher('kolobok.txt', cipher_choice, key_params)
            
            if encrypted and decrypted:
                print("\n" + "="*70)
                print("РЕЗУЛЬТАТЫ ОБРАБОТКИ ФАЙЛА")
                print("="*70)
                
                print(f"\nЗАШИФРОВАННЫЙ ТЕКСТ (первые 200 символов):")
                print(print_sample(encrypted, 200))
                
                print(f"\nРАСШИФРОВАННЫЙ ТЕКСТ (первые 200 символов):")
                print(print_sample(decrypted, 200))
                
                # Проверка успешности
                if cipher_choice == '1':
                    original_clean = read_file('kolobok.txt').upper().replace('Ё', 'Е')
                    decrypted_clean = decrypted.rstrip('Ъ')
                    if original_clean.startswith(decrypted_clean[:len(original_clean)]):
                        print("\n✓ Расшифровка успешна!")
                    else:
                        print("\n✗ Ошибка расшифровки")
                else:
                    original_text = read_file('kolobok.txt')
                    cipher = PlayfairCipher(key_params)
                    original_clean = cipher._clean_text(original_text)
                    if original_clean == decrypted:
                        print("\n✓ Расшифровка успешна!")
                    else:
                        print("\n✗ Ошибка расшифровки")
                
                save_choice = input("\nСохранить результаты в файлы? (y/n): ").strip().lower()
                if save_choice == 'y':
                    results_dir = "file_results"
                    if not os.path.exists(results_dir):
                        os.makedirs(results_dir)
                    
                    if cipher_choice == '1':
                        enc_filename = f"{results_dir}/encrypted_matrix.txt"
                        dec_filename = f"{results_dir}/decrypted_matrix.txt"
                    else:
                        enc_filename = f"{results_dir}/encrypted_playfair.txt"
                        dec_filename = f"{results_dir}/decrypted_playfair.txt"
                    
                    save_to_file(enc_filename, encrypted)
                    save_to_file(dec_filename, decrypted)
            
            input("\nНажмите Enter для продолжения...")
        
        else:
            print("Неверный выбор. Пожалуйста, выберите 0-3.")


if __name__ == "__main__":
    main()