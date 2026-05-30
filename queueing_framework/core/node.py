from dataclasses import dataclass, field
from typing import Optional, Dict
from queueing_framework.core.queue import QueueBuffer, QueueDiscipline
from queueing_framework.distributions.distributions import Distribution


@dataclass
class Source:
    """
    Источник заявок. Генерирует поток заявок в целевой узел.
    """
    source_id: str                   # уникальное имя источника
    target_node_ids: list            # в какие узлы направляет заявки
    arrival_dist: Distribution       # распределение интервалов поступления


class ServiceNode:
    """
    Узел сети СМО. Содержит очередь и один или несколько серверов.
    """

    def __init__(
        self,
        node_id: str,
        service_dist: Distribution,
        num_servers: Optional[int] = 1,
        system_capacity: Optional[int] = None,
        discipline: QueueDiscipline = QueueDiscipline.FIFO,
        routing: Optional[Dict[str, float]] = None
    ):
        self.node_id = node_id

        # распределение времени обслуживания
        self.service_dist = service_dist

        # num_servers=None означает бесконечное число серверов (M/M/inf)
        self.num_servers = num_servers

        # system_capacity=None означает неограниченную систему
        self.system_capacity = system_capacity

        self.discipline = discipline

        # routing — словарь маршрутов: {"node_id": вероятность, "EXIT": вероятность}
        self.routing = routing if routing is not None else {}

        # вычисляем ёмкость очереди из ёмкости системы
        if system_capacity is not None and num_servers is not None:
            queue_capacity = max(0, system_capacity - num_servers)
        else:
            queue_capacity = None

        self.queue = QueueBuffer(
            capacity=queue_capacity,
            discipline=discipline
        )

        # текущее число занятых серверов
        self.busy_servers: int = 0

    @property
    def in_system(self) -> int:
        """Текущее число заявок в системе (в очереди + на обслуживании)."""
        return len(self.queue) + self.busy_servers

    def has_free_server(self) -> bool:
        """Есть ли свободный сервер?"""
        if self.num_servers is None:
            return True   # бесконечное число серверов — всегда есть
        return self.busy_servers < self.num_servers

    def can_accept(self) -> bool:
        """Может ли узел принять новую заявку (не переполнен)?"""
        if self.system_capacity is None:
            return True   # неограниченная система
        return self.in_system < self.system_capacity

    def __repr__(self) -> str:
        return (f"ServiceNode(id={self.node_id}, "
                f"servers={self.num_servers}, "
                f"in_system={self.in_system}, "
                f"capacity={self.system_capacity})")