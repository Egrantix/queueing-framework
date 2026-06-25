"""
Точка входа: запускает все примеры по очереди.
"""
import sys
from examples import mm1, mmn, mm1k, network_example


def main():
    examples = {
        '1': ('M/M/1 — одноканальная система', mm1.run),
        '2': ('M/M/n — многоканальная система', mmn.run),
        '3': ('M/M/1/K — система с ограниченным буфером', mm1k.run),
        '4': ('Сеть СМО — 3 узла', network_example.run),
    }

    print("\n╔══════════════════════════════════════════════╗")
    print("║  Библиотека моделирования сетей СМО           ║")
    print("╚══════════════════════════════════════════════╝\n")

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Выберите пример:")
        for k, (name, _) in examples.items():
            print(f"  {k}. {name}")
        print("  0. Запустить все\n")
        choice = input("Номер примера: ").strip()

    if choice == '0':
        for k, (name, fn) in examples.items():
            print(f"\n{'─'*50}")
            print(f"  Пример {k}: {name}")
            print('─'*50)
            fn()
    elif choice in examples:
        name, fn = examples[choice]
        print(f"\nЗапуск: {name}\n")
        fn()
    else:
        print("Неверный выбор.")


if __name__ == '__main__':
    main()