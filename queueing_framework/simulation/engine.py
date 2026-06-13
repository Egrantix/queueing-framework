import numpy as np
from queueing_framework.core.event import Event, EventType, EventQueue
from queueing_framework.core.request import Request
from queueing_framework.network.network import QueueingNetwork
import random

class SimulationEngine:
    """
    Дискретно-событийный симулятор сети СМО.
    Работает по принципу «следующего события»:
    всегда обрабатывает ближайшее по времени событие из календаря.
    """

    def __init__(
        self,
        network: QueueingNetwork,
        sim_time: float,
        warmup_time: float = 0.0,
        seed: int = 42
    ):
        self.network = network
        self.sim_time = 0       # время окончания моделирования
        self.warmup_time = warmup_time # период прогрева (не учитывается в статистике)

        # генератор случайных чисел с фиксированным зерном
        self.rng = np.random.default_rng(seed)

        self.clock = 0.0               # текущее модельное время
        self._request_counter = 0      # счётчик для уникальных ID заявок
        self.calendar = EventQueue()   # календарь событий

        # сборщик статистики создаётся при запуске
        self.collector = None

    def _new_request(self) -> Request:
        """Создать новую заявку с уникальным ID."""
        self._request_counter += 1
        return Request(self._request_counter, self.clock)

    def _schedule(self, event: Event) -> None:
        """Добавить событие в календарь, если оно в пределах sim_time."""
        if event.time <= self.sim_time:
            self.calendar.push(event)

    def _record_state(self, node_id: str) -> None:
        """Записать текущее состояние узла в сборщик статистики."""
        node = self.network.nodes[node_id]
        self.collector.record_state(
            node_id,
            self.clock,
            len(node.queue),
            node.busy_servers
        )

    def _initialize(self, clean_up: bool = True) -> None:
        """
        Инициализация: запланировать первое поступление
        от каждого источника и событие конца прогрева.
        """
        for src in self.network.sources.values():
            t = self.clock + src.arrival_dist.sample(self.rng)
            self._schedule(Event(
                time=t,
                priority=1,
                event_type=EventType.ARRIVAL,
                node_id=random.choice(src.target_node_ids),
                source_id=src.source_id
            ))

        if self.warmup_time > 0 and clean_up:
            self._schedule(Event(
                time=self.warmup_time,
                priority=0,
                event_type=EventType.WARMUP_END
            ))

    def _handle_arrival(self, event: Event) -> None:
        """
        Обработка поступления заявки в узел.
        1. Создаём заявку (или берём переданную из маршрута)
        2. Планируем следующее поступление от источника
        3. Если узел переполнен — DROP
        4. Если есть свободный сервер — сразу на обслуживание
        5. Иначе — в очередь
        """
        node = self.network.get_node(event.node_id)

        # если заявка пришла из маршрута — берём её, иначе создаём новую
        request = event.request if event.request else self._new_request()

        # фиксируем время прихода в этот узел
        request.arrival_times[node.node_id] = self.clock
        request.route.append(node.node_id)

        # учитываем поступление в статистике
        self.collector.record_arrival(node.node_id)
        self._record_state(node.node_id)

        # планируем следующее поступление от того же источника
        if event.source_id:
            src = self.network.sources[event.source_id]
            next_arrival = self.clock + src.arrival_dist.sample(self.rng)
            self._schedule(Event(
                time=next_arrival,
                priority=1,
                event_type=EventType.ARRIVAL,
                node_id=random.choice(src.target_node_ids),
                source_id=src.source_id
            ))

        # узел переполнен — отказ
        if not node.can_accept():
            request.dropped = True
            request.dropped_at_node = node.node_id
            self.collector.record_drop(node.node_id)
            self._record_state(node.node_id)
            return

        # есть свободный сервер — сразу начинаем обслуживание
        if node.has_free_server():
            node.busy_servers += 1
            request.service_start_times[node.node_id] = self.clock
            service_time = node.service_dist.sample(self.rng)
            self._schedule(Event(
                time=self.clock + service_time,
                priority=2,
                event_type=EventType.SERVICE_END,
                node_id=node.node_id,
                request=request
            ))
        else:
            # сервер занят — заявка встаёт в очередь
            node.queue.enqueue(request)

        self._record_state(node.node_id)

    def _handle_service_end(self, event: Event) -> None:
        """
        Обработка завершения обслуживания.
        1. Фиксируем время окончания, передаём в статистику
        2. Освобождаем сервер
        3. Берём следующую заявку из очереди (если есть)
        4. Маршрутизируем обслуженную заявку
        """
        node = self.network.get_node(event.node_id)
        request = event.request

        request.service_end_times[node.node_id] = self.clock

        # передаём данные в сборщик статистики
        self.collector.record_service_end(
            node.node_id,
            request.arrival_times[node.node_id],
            request.service_start_times[node.node_id],
            self.clock
        )

        node.busy_servers -= 1
        self._record_state(node.node_id)

        # берём следующую заявку из очереди
        next_request = node.queue.dequeue(self.rng)
        if next_request:
            node.busy_servers += 1
            next_request.service_start_times[node.node_id] = self.clock
            service_time = node.service_dist.sample(self.rng)
            self._schedule(Event(
                time=self.clock + service_time,
                priority=2,
                event_type=EventType.SERVICE_END,
                node_id=node.node_id,
                request=next_request
            ))
            self._record_state(node.node_id)

        # маршрутизируем обслуженную заявку
        self._route(request, node)

    def _route(self, request: Request, node) -> None:
        """
        Маршрутизация заявки после обслуживания.
        Выбираем следующий узел по вероятностям из routing.
        """
        if not node.routing:
            request.departure_time = self.clock
            return

        destinations = list(node.routing.keys())
        probabilities = list(node.routing.values())

        chosen = str(self.rng.choice(destinations, p=probabilities))

        if chosen == "EXIT":
            request.departure_time = self.clock
        else:
            # планируем мгновенное прибытие в следующий узел
            self._schedule(Event(
                time=self.clock,
                priority=1,
                event_type=EventType.ARRIVAL,
                node_id=chosen,
                request=request
            ))

    def run(self, sim_time: float = 0, clean_up: bool = True):
        """
        Запустить моделирование.
        Возвращает объект StatisticsCollector с данными.
        """
        from queueing_framework.statistics.collector import StatisticsCollector
        
        
        if not clean_up:
            self.sim_time += sim_time
            print("Running simulation without clean-up. Previous statistics will be preserved.")
        else:
            self.sim_time = sim_time
            print("Running simulation with clean-up. Previous statistics will be reset.")
        if self.collector is None or clean_up:
            self.collector = StatisticsCollector(
                node_ids=self.network.node_ids(),
                warmup_time=self.warmup_time
            )
        
        self._initialize(clean_up=clean_up)

        # главный цикл симуляции
        while not self.calendar.is_empty():
            if self.clock % 50 < 1e-2: 
                print(f"Processing event at time {self.clock:.2f}, "
                      f"events left: {len(self.calendar)}", end='\r')
            event = self.calendar.pop()

            if event.time > self.sim_time:
                break

            self.clock = event.time

            if event.event_type == EventType.ARRIVAL:
                self._handle_arrival(event)
            elif event.event_type == EventType.SERVICE_END:
                self._handle_service_end(event)
            elif event.event_type == EventType.WARMUP_END:
                self.collector.notify_warmup_end(self.clock)
        print(self.collector.arrivals)
        return self.collector