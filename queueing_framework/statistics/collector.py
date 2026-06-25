from typing import Dict, List, Tuple, Optional


class StatisticsCollector:
    """
    Сборщик статистики симуляции.
    Накапливает данные по каждому узлу на протяжении всего моделирования.
    После периода прогрева (warmup) — сбрасывает накопленные данные
    и начинает собирать статистику заново.
    """

    def __init__(self, node_ids: List[str], warmup_time: float = 0.0):
        self.node_ids = node_ids
        self.warmup_time = warmup_time

        # флаг: закончился ли период прогрева
        self._warmup_done = (warmup_time == 0.0)

        # момент начала сбора «чистой» статистики
        self._stats_start_time: float = warmup_time

        # история длины очереди: список пар (время, значение)
        self.queue_length_history: Dict[str, List[Tuple[float, int]]] = {
            n: [] for n in node_ids
        }

        # история числа занятых серверов: список пар (время, значение)
        self.busy_servers_history: Dict[str, List[Tuple[float, int]]] = {
            n: [] for n in node_ids
        }

        # счётчики заявок
        self.arrivals: Dict[str, int] = {n: 0 for n in node_ids}
        self.served: Dict[str, int] = {n: 0 for n in node_ids}
        self.dropped: Dict[str, int] = {n: 0 for n in node_ids}

        # времена ожидания в очереди (SERVICE_START - ARRIVAL)
        self.wait_times: Dict[str, List[float]] = {n: [] for n in node_ids}

        # времена пребывания в системе (SERVICE_END - ARRIVAL)
        self.sojourn_times: Dict[str, List[float]] = {n: [] for n in node_ids}

        # суммарное время занятости серверов
        self.busy_time: Dict[str, float] = {n: 0.0 for n in node_ids}

    def notify_warmup_end(self, current_time: float) -> None:
        """
        Вызывается в момент окончания периода прогрева.
        Сбрасывает все накопленные данные — статистика считается заново.
        """
        self._warmup_done = True
        self._stats_start_time = current_time

        for n in self.node_ids:
            self.arrivals[n] = 0
            self.served[n] = 0
            self.dropped[n] = 0
            self.wait_times[n] = []
            self.sojourn_times[n] = []
            self.busy_time[n] = 0.0
            # историю состояний НЕ сбрасываем — она нужна для расчёта площадей

    def record_state(
        self,
        node_id: str,
        time: float,
        queue_length: int,
        busy_servers: int
    ) -> None:
        """
        Записать текущее состояние узла (длину очереди и занятость серверов).
        Вызывается при каждом изменении состояния узла.
        """
        self.queue_length_history[node_id].append((time, queue_length))
        self.busy_servers_history[node_id].append((time, busy_servers))

    def record_arrival(self, node_id: str) -> None:
        """Зафиксировать поступление заявки."""
        if self._warmup_done:
            self.arrivals[node_id] += 1

    def record_drop(self, node_id: str) -> None:
        """Зафиксировать отказ (потерю заявки)."""
        if self._warmup_done:
            self.dropped[node_id] += 1

    def record_service_end(
        self,
        node_id: str,
        arrival_time: float,
        service_start_time: float,
        service_end_time: float
    ) -> None:
        """
        Зафиксировать завершение обслуживания.
        Вычисляет время ожидания и время пребывания.
        """
        if self._warmup_done:
            self.served[node_id] += 1

            wait = service_start_time - arrival_time
            sojourn = service_end_time - arrival_time

            self.wait_times[node_id].append(wait)
            self.sojourn_times[node_id].append(sojourn)
            self.busy_time[node_id] += service_end_time - service_start_time