import runpy
from pathlib import Path


BASE_DIR = Path(__file__).parent


def run_script(relative_path):
    
    try:
        path = BASE_DIR / relative_path

        print("\n" + "=" * 60)
        print(f"Запуск: {path.name}")
        print("=" * 60 + "\n")

        runpy.run_path(str(path), run_name="__main__")

    except FileNotFoundError:
        print(f"\nФайл не найден:\n{path}")

    except Exception as e:
        print(f"\nОшибка:\n{e}")

    input("\nНажмите Enter для продолжения...")


# ==========================
# КЛАССИЧЕСКИЕ ШИФРЫ
# ==========================

def classic_menu():
    while True:

        print("\n" + "=" * 60)
        print("КЛАССИЧЕСКИЕ ШИФРЫ")
        print("=" * 60)

        print("1 - Атбаш")
        print("2 - Цезарь")
        print("3 - Полибий")
        print("4 - Тритемий")
        print("5 - Виженер")
        print("6 - Вертикальная перестановка")
        print("7 - Матричный шифр")
        print("8 - Плейфер")
        print("0 - Назад")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            run_script("Лабы Тема 1/Лаб 1_1/1.Шифр Атбаш.py")

        elif choice == "2":
            run_script("Лабы Тема 1/Лаб 1_1/2.Шифр Цезаря.py")

        elif choice == "3":
            run_script("Лабы Тема 1/Лаб 1_1/3.Квадрат Полибия.py")

        elif choice == "4":
            run_script("Лабы Тема 1/Лаб 1_2/4.Шифр Тритемия.py")

        elif choice == "5":
            run_script("Лабы Тема 1/Лаб 1_2/5.Шифр Виженера.py")

        elif choice == "6":
            run_script("Лабы Тема 1/Лаб 1_4/10.Вертикальная перестановка.py")

        elif choice == "7":
            run_script("Лабы Тема 1/Лаб 1_3/8.Матричный шифр.py")

        elif choice == "8":
            run_script("Лабы Тема 1/Лаб 1_3/9.Шифр Плейфера.py")

        elif choice == "0":
            return


# ==========================
# СИММЕТРИЧНЫЕ АЛГОРИТМЫ
# ==========================

def symmetric_menu():

    while True:

        print("\n" + "=" * 60)
        print("СИММЕТРИЧНЫЕ АЛГОРИТМЫ")
        print("=" * 60)

        print("1 - Блокнот Шеннона")
        print("2 - A5/1")
        print("3 - A5/2")
        print("4 - AES")
        print("0 - Назад")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            run_script("Лабы Тема 1/Лаб 1_5/13.Одноразовый блокнот К.Шеннона.py")

        elif choice == "2":
            run_script("Лабы Тема 1/Лаб 1_6/15.A5_1.py")

        elif choice == "3":
            run_script("Лабы Тема 1/Лаб 1_6/16.A5_2.py")

        elif choice == "4":
            run_script("Лабы Тема 1/Лаб 1_7/19.AES.py")

        elif choice == "0":
            return


# ==========================
# АСИММЕТРИЧНЫЕ
# ==========================

def asymmetric_menu():

    while True:

        print("\n" + "=" * 60)
        print("АСИММЕТРИЧНЫЕ АЛГОРИТМЫ")
        print("=" * 60)

        print("1 - RSA")
        print("2 - ElGamal")
        print("3 - ECC")
        print("4 - Диффи-Хеллман")
        print("0 - Назад")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            run_script("Лабы Тема 3/Лаб 3_1/24.RSA.py")

        elif choice == "2":
            run_script("Лабы Тема 3/Лаб 3_1/21-23.RSA_Elgamal_ECC.py")

        elif choice == "3":
            run_script("Лабы Тема 3/Лаб 3_1/21-23.RSA_Elgamal_ECC.py")

        elif choice == "4":
            run_script("Лабы Тема 2/Лаб 2_2/20.Диффи-Хеллман.py")

        elif choice == "0":
            return


# ==========================
# ЭЛЕКТРОННАЯ ПОДПИСЬ
# ==========================

def signature_menu():

    while True:

        print("\n" + "=" * 60)
        print("ЭЛЕКТРОННАЯ ПОДПИСЬ")
        print("=" * 60)

        print("1 - RSA подпись")
        print("2 - ГОСТ Р 34.10-94")
        print("0 - Назад")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            run_script("Лабы Тема 3/Лаб 3_1/24.RSA.py")

        elif choice == "2":
            run_script("Лабы Тема 3/Лаб 3_2/26.ГОСТ_Р_34.10-94.py")

        elif choice == "0":
            return


# ==========================
# ГЛАВНОЕ МЕНЮ
# ==========================

def main():

    while True:

        print("\n")
        print("=" * 60)
        print("ГЛАВНОЕ МЕНЮ КРИПТОГРАФИЧЕСКИХ АЛГОРИТМОВ")
        print("=" * 60)

        print("1 - Классические шифры")
        print("2 - Симметричные алгоритмы")
        print("3 - Асимметричные алгоритмы")
        print("4 - Электронная подпись")
        print("0 - Выход")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            classic_menu()

        elif choice == "2":
            symmetric_menu()

        elif choice == "3":
            asymmetric_menu()

        elif choice == "4":
            signature_menu()

        elif choice == "0":
            print("\nДо свидания!")
            break

        else:
            print("\nНеверный выбор")


if __name__ == "__main__":
    main()

