# Queueing Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-educational-yellow)]()

Библиотека дискретно-событийного моделирования сетей массового обслуживания (СМО), разработанная в рамках выпускной квалификационной работы по направлению «Программная инженерия».

---

## Возможности

- Моделирование классических систем: **M/M/1**, **M/M/n**, **M/M/1/K**, **M/M/n/K**, **M/G/1**, **G/G/1**
- Построение сетей СМО произвольной топологии с **вероятностной маршрутизацией**
- Три дисциплины обслуживания очереди: **FIFO**, **LIFO**, **SIRO**
- **Период прогрева** для устранения влияния начальных условий
- Автоматический расчёт показателей эффективности: ρ, L, Lq, W, Wq, X, P_loss
- **Визуализация**: динамика очереди, гистограмма времени ожидания, граф топологии сети

---

## Требования

- Python 3.10+
- numpy >= 1.24
- matplotlib >= 3.7
- networkx >= 3.1

---

## Установка

```bash
git clone https://github.com/ваш-username/queueing-framework.git
cd queueing-framework
pip install numpy matplotlib networkx
```

Никаких дополнительных зависимостей и сборки не требуется.

---

## Быстрый старт

```python
from queueing_framework.network.network import QueueingNetwork
from queueing_framework.core.node import ServiceNode, Source
from queueing_framework.distributions.distributions import Exponential
from queueing_framework.simulation.engine import SimulationEngine
from queueing_framework.metrics.performance import MetricsCalculator

# Строим сеть M/M/1: λ=4, μ=5
net = QueueingNetwork()
net.add_node(ServiceNode('server', Exponential(5.0), num_servers=1, routing={'EXIT': 1.0}))
net.add_source(Source('src', 'server', Exponential(4.0)))

# Запускаем симуляцию
engine = SimulationEngine(net, sim_time=5000.0, warmup_time=200.0, seed=42)
col = engine.run()

# Получаем метрики
calc = MetricsCalculator(col, sim_end=5000.0, network=net)
calc.print_report('server')

# Вывод:
# ρ  = 0.7999  |  L  = 4.054  |  Lq = 3.254
# W  = 1.019   |  Wq = 0.818  |  X  = 3.978
```

---

## Запуск примеров

```bash
python main.py 1   # M/M/1   — одноканальная система
python main.py 2   # M/M/n   — многоканальная система
python main.py 3   # M/M/1/K — система с ограниченным буфером
python main.py 4   # Сеть СМО — 3 узла
```

Или запускать примеры напрямую:

```bash
python examples/mm1.py
python examples/mmn.py
python examples/mm1k.py
python examples/network_example.py
```

Через Jupyter Notebook / Google Colab:

```python
%run examples/mm1.py
```

---

## Поддерживаемые распределения

| Класс                        | Распределение          |
|------------------------------|------------------------|
| `Exponential(rate)`          | Экспоненциальное       |
| `Uniform(a, b)`              | Равномерное            |
| `Normal(mean, std)`          | Нормальное             |
| `Deterministic(val)`         | Детерминированное      |
| `Erlang(k, rate)`            | Эрланга                |
| `HyperExponential(rates, p)` | Гиперэкспоненциальное  |

---

## Структура проекта

```
queueing_framework/
│
├── core/
│   ├── event.py          # Event, EventType, EventQueue (календарь событий)
│   ├── request.py        # Request (заявка с историей маршрута)
│   ├── queue.py          # QueueBuffer, QueueDiscipline
│   └── node.py           # ServiceNode (узел СМО), Source (источник)
│
├── distributions/
│   └── distributions.py  # Exponential, Uniform, Normal, Deterministic,
│                         # HyperExponential, Erlang, базовый класс Distribution
│
├── network/
│   └── network.py        # QueueingNetwork — топология сети, валидация маршрутов
│
├── simulation/
│   └── engine.py         # SimulationEngine — главный цикл дискретных событий
│
├── statistics/
│   └── collector.py      # StatisticsCollector — история состояний узлов
│
├── metrics/
│   └── performance.py    # MetricsCalculator, NodeMetrics — расчёт ρ, L, Lq, W, Wq
│
└── visualization/
    └── plots.py          # Visualizer — графики очереди, гистограммы, граф сети

examples/
├── mm1.py                # M/M/1 — одноканальная система
├── mmn.py                # M/M/n — многоканальная система
├── mm1k.py               # M/M/1/K — система с ограниченным буфером
└── network_example.py    # Сеть из 3 узлов с маршрутизацией

main.py                   # Точка входа, меню выбора примера
README.md
.gitignore
```

---

## Верификация

Результаты симуляции сравнивались с аналитическими формулами теории СМО. Погрешность не превышает **2.3%** для всех протестированных моделей.

### M/M/1 (λ=4, μ=5, sim_time=5000)

| Метрика | Симуляция | Аналитика | Погрешность |
|:-------:|:---------:|:---------:|:-----------:|
| ρ       | 0.7999    | 0.8000    | 0.01%       |
| L       | 4.0536    | 4.0000    | 1.3%        |
| Lq      | 3.2538    | 3.2000    | 1.7%        |
| W       | 1.0191    | 1.0000    | 1.9%        |
| Wq      | 0.8180    | 0.8000    | 2.3%        |
| X       | 3.9779    | 4.0000    | 0.6%        |

Верификация выполнена также для моделей **M/M/n** и **M/M/1/K** — результаты аналогичны.

---

## Автор

**Булатов Евгений Владимирович**  
РТУ МИРЭА, Институт информационных технологий, кафедра № 231  
ВКР по направлению 09.04.04 «Программная инженерия», 2026

---

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
