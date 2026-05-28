# Queueing Framework

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


## Запуск примеров

```bash
python main.py 1   # M/M/1   — одноканальная система
python main.py 2   # M/M/n   — многоканальная система
python main.py 3   # M/M/1/K — система с ограниченным буфером
python main.py 4   # Сеть СМО — 3 узла
```

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
```

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

Результаты симуляции для модели M/M/1 (λ=4, μ=5, sim_time=5000):

| Метрика | Симуляция | Аналитика | Погрешность |
|:-------:|:---------:|:---------:|:-----------:|
| ρ       | 0.7999    | 0.8000    | 0.01%       |
| L       | 4.0536    | 4.0000    | 1.3%        |
| Lq      | 3.2538    | 3.2000    | 1.7%        |
| W       | 1.0191    | 1.0000    | 1.9%        |
| Wq      | 0.8180    | 0.8000    | 2.3%        |
| X       | 3.9779    | 4.0000    | 0.6%        |

Погрешность не превышает **2.3%** — результаты соответствуют теоретическим значениям.
