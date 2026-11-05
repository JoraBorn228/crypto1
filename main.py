import runpy
from pathlib import Path


BASE_DIR = Path(__file__).parent


def run_script(relative_path):
    path = BASE_DIR / relative_path
    try:
        print("\n" + "=" * 60)
        print(f"Запуск: {path.name}")
        print("=" * 60 + "\n")
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit:
        # Возврат в меню, если вложенная лабораторная программа вызвала exit.
        pass
    except FileNotFoundError:
        print(f"\nФайл не найден:\n{path}")
    except Exception as exc:
        print(f"\nОшибка:\n{exc}")
    input("\nНажмите Enter для продолжения...")


def classic_menu():
    options = {
        "1": ("Атбаш", "Лабы Тема 1/Лаб 1_1/1.Шифр Атбаш.py"),
        "2": ("Белазо", "Лабы Тема 1/Лаб 1_2/5.Шифр Белазо.py"),
        "3": ("Матричный шифр", "Лабы Тема 1/Лаб 1_3/8.Матричный шифр.py"),
        "4": ("Вертикальная перестановка", "Лабы Тема 1/Лаб 1_4/10.Вертикальная перестановка.py"),
    }
    while True:
        print("\n" + "=" * 60)
        print("КЛАССИЧЕСКИЕ ШИФРЫ")
        print("=" * 60)
        for number, (name, _) in options.items():
            print(f"{number} - {name}")
        print("0 - Назад")
        choice = input("\nВаш выбор: ").strip()
        if choice == "0":
            return
        if choice in options:
            run_script(options[choice][1])
        else:
            print("Неверный выбор")


def symmetric_menu():
    options = {
        "1": ("Одноразовый блокнот Шеннона", "Лабы Тема 1/Лаб 1_5/13.Одноразовый блокнот К.Шеннона.py"),
        "2": ("A5/1", "Лабы Тема 1/Лаб 1_6/15.A5_1.py"),
        "3": ("AES", "Лабы Тема 1/Лаб 1_7/19.AES.py"),
    }
    while True:
        print("\n" + "=" * 60)
        print("СИММЕТРИЧНЫЕ АЛГОРИТМЫ")
        print("=" * 60)
        for number, (name, _) in options.items():
            print(f"{number} - {name}")
        print("0 - Назад")
        choice = input("\nВаш выбор: ").strip()
        if choice == "0":
            return
        if choice in options:
            run_script(options[choice][1])
        else:
            print("Неверный выбор")


def asymmetric_menu():
    options = {
        "1": ("RSA (шифрование)", "Лабы Тема 2/Лаб 2_1/21-23.RSA_Elgamal_ECC.py"),
        "2": ("Диффи—Хеллман", "Лабы Тема 4/Лаб 4_1/28.Диффи-Хеллман.py"),
    }
    while True:
        print("\n" + "=" * 60)
        print("АСИММЕТРИЧНЫЕ АЛГОРИТМЫ И ОБМЕН КЛЮЧАМИ")
        print("=" * 60)
        for number, (name, _) in options.items():
            print(f"{number} - {name}")
        print("0 - Назад")
        choice = input("\nВаш выбор: ").strip()
        if choice == "0":
            return
        if choice in options:
            run_script(options[choice][1])
        else:
            print("Неверный выбор")


def signature_menu():
    options = {
        "1": ("Цифровая подпись RSA", "Лабы Тема 3/Лаб 3_1/24.RSA.py"),
        "2": ("ГОСТ Р 34.10-2012", "Лабы Тема 3/Лаб 3_2/27.ГОСТ_Р_34.10-2012.py"),
    }
    while True:
        print("\n" + "=" * 60)
        print("ЭЛЕКТРОННАЯ ПОДПИСЬ")
        print("=" * 60)
        for number, (name, _) in options.items():
            print(f"{number} - {name}")
        print("0 - Назад")
        choice = input("\nВаш выбор: ").strip()
        if choice == "0":
            return
        if choice in options:
            run_script(options[choice][1])
        else:
            print("Неверный выбор")


def main():
    menus = {
        "1": ("Классические шифры", classic_menu),
        "2": ("Симметричные алгоритмы", symmetric_menu),
        "3": ("Асимметричные алгоритмы и обмен ключами", asymmetric_menu),
        "4": ("Электронная подпись", signature_menu),
    }
    while True:
        print("\n" + "=" * 60)
        print("ГЛАВНОЕ МЕНЮ КРИПТОГРАФИЧЕСКИХ АЛГОРИТМОВ")
        print("=" * 60)
        for number, (name, _) in menus.items():
            print(f"{number} - {name}")
        print("0 - Выход")
        choice = input("\nВаш выбор: ").strip()
        if choice == "0":
            print("\nДо свидания!")
            break
        if choice in menus:
            menus[choice][1]()
        else:
            print("\nНеверный выбор")


if __name__ == "__main__":
    main()
