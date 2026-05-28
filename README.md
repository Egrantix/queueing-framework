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
│
├── core/
│ ├── event.py # Классы Event, EventType, EventQueue (календарь событий)
│ ├── request.py # Класс Request (заявка с историей маршрута)
│ ├── queue.py # Класс QueueBuffer, перечисление QueueDiscipline
│ └── node.py # Классы ServiceNode (узел СМО) и Source (источник)
│
├── distributions/
│ └── distributions.py # Exponential, Uniform, Normal, Deterministic,
│ # HyperExponential, Erlang и базовый класс Distribution
│
├── network/
│ └── network.py # Класс QueueingNetwork — топология сети, валидация маршрутов
│
├── simulation/
│ └── engine.py # Класс SimulationEngine — главный цикл дискретных событий
│
├── statistics/
│ └── collector.py # Класс StatisticsCollector — сбор истории состояний
│
├── metrics/
│ └── performance.py # Классы MetricsCalculator и NodeMetrics — расчёт ρ, L, Lq, W, Wq
│
└── visualization/
└── plots.py # Класс Visualizer — графики очереди, гистограммы, граф сети

examples/
├── mm1.py # Пример: M/M/1, сравнение с аналитикой
├── mmn.py # Пример: M/M/n (3 сервера)
├── mm1k.py # Пример: M/M/1/K (ограниченный буфер, отказы)
└── network_example.py # Пример: сеть из 3 узлов с маршрутизацией