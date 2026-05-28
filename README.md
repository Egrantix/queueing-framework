# Queueing Framework

Библиотека дискретно-событийного моделирования сетей массового обслуживания (СМО).

## Установка зависимостей

pip install numpy matplotlib networkx scipy

## Быстрый старт

python main.py 1   # M/M/1
python main.py 2   # M/M/n
python main.py 3   # M/M/1/K
python main.py 4   # Сеть СМО — 3 узла

## Структура проекта

queueing_framework/
├── core/           # Доменная модель (заявки, события, очередь)
├── distributions/  # Вероятностные распределения
├── network/        # Топология сети СМО
├── simulation/     # Движок симуляции
├── statistics/     # Сборщик статистики
├── metrics/        # Расчёт характеристик
└── visualization/  # Графики и визуализация