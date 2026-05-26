"""
ШИФР ЦЕЗАРЯ
Русский алфавит (33 буквы с Ъ)
Сдвиг на K позиций по кольцу алфавита (K можно изменить под вариант задания).
Добавлена проверка на 1000 символов с текстом из книги.
"""

ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
N = len(ALPHABET)

K = 7

char_to_num = {char: i for i, char in enumerate(ALPHABET)}
num_to_char = {i: char for i, char in enumerate(ALPHABET)}


def validate_1000_chars(text, min_chars=1000):
    """
    Проверяет, что текст содержит не менее min_chars символов.
    Возвращает кортеж (результат проверки, количество символов).
    """
    char_count = len(text)
    return char_count >= min_chars, char_count


def encrypt(text):
    text = text.upper()
    result = []
    for char in text:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            m = char_to_num[char]
            L = (m + K) % N
            result.append(num_to_char[L])
        else:
            result.append(char)
    return ''.join(result)


def decrypt(ciphertext):
    ciphertext = ciphertext.upper()
    result = []
    for char in ciphertext:
        if char == ' ':
            result.append(' ')
        elif char in char_to_num:
            L = char_to_num[char]
            m = (L - K) % N
            result.append(num_to_char[m])
        else:
            result.append(char)
    return ''.join(result)


BOOK_TEXT_1000 = """Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему. Всё смешалось в доме Облонских. Жена узнала, что муж был в связи с бывшею в их доме француженкою-гувернанткой, и объявила мужу, что не может жить с ним в одном доме. Положение это продолжалось уже третий день и мучительно чувствовалось и самими супругами, и всеми членами семьи, и домочадцами. Все члены семьи и домочадцы чувствовали, что нет смысла в их сожительстве и что на каждом постоялом дворе случайно сошедшиеся люди более связаны между собой, чем они, члены семьи и домочадцы Облонских. Жена не выходила из своих комнат, мужа третий день не было дома. Дети бегали по всему дому, как потерянные; англичанка поссорилась с экономкой и написала записку приятельнице, прося приискать ей новое место; повар ушёл ещё вчера со двора, во время обеда; черная кухарка и кучер просили расчёта.
Л.Н. Толстой, Анна Каренина"""


original = "ЛЕОПАРД НЕ МОЖЕТ ИЗМЕНИТЬ СВОИХ ПЯТЕН"

print("=" * 60)
print("ШИФР ЦЕЗАРЯ")
print("=" * 60)
print(f"Сдвиг K = {K}")
print(f"Исходный текст: {original}")
encrypted = encrypt(original)
print(f"Зашифровано: {encrypted}")
print("-" * 60)
decrypted = decrypt(encrypted)
print(f"Расшифровано: {decrypted}")
print("-" * 60)
print(f"Совпадение: {original == decrypted}")
print("=" * 60)

print("\n" + "=" * 60)
print("ПРОВЕРКА НА 1000 СИМВОЛОВ")
print("=" * 60)

is_valid, char_count = validate_1000_chars(BOOK_TEXT_1000)
print(f"Текст из книги (Л.Н. Толстой, 'Анна Каренина'):")
print(f"Количество символов: {char_count}")
print(f"Проверка на 1000 символов: {'ПРОЙДЕНА' if is_valid else 'НЕ ПРОЙДЕНА'}")
print("-" * 60)

encrypted_book = encrypt(BOOK_TEXT_1000)
print(f"Зашифрованный текст (первые 200 символов):")
print(encrypted_book[:200] + "...")
print("-" * 60)

decrypted_book = decrypt(encrypted_book)
print(f"Расшифрованный текст (первые 200 символов):")
print(decrypted_book[:200] + "...")
print("-" * 60)

print(f"Совпадение после расшифровки: {BOOK_TEXT_1000.upper() == decrypted_book}")
print("=" * 60)
