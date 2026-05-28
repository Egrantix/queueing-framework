import heapq
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from queueing_framework.core.request import Request


class EventType(Enum):
    """Типы событий в дискретно-событийной модели."""
    ARRIVAL = auto()        # поступление заявки в узел
    SERVICE_START = auto()  # начало обслуживания
    SERVICE_END = auto()    # завершение обслуживания
    ROUTE = auto()          # маршрутизация между узлами
    DEPARTURE = auto()      # выход заявки из сети
    DROP = auto()           # потеря заявки (очередь переполнена)
    STAT_SAMPLE = auto()    # периодическая запись состояния системы
    WARMUP_END = auto()     # конец периода прогрева


@dataclass(order=True)
class Event:
    """
    Событие в календаре симулятора.
    Сортируется по времени — ближайшее событие обрабатывается первым.
    """
    time: float                          # момент наступления события
    priority: int = 0                    # приоритет (меньше = важнее)
    event_type: EventType = field(
        compare=False,
        default=EventType.ARRIVAL
    )
    node_id: Optional[str] = field(
        compare=False,
        default=None
    )
    request: Optional[object] = field(
        compare=False,
        default=None
    )
    source_id: Optional[str] = field(
        compare=False,
        default=None
    )


class EventQueue:
    """
    Календарь событий на основе двоичной кучи (heapq).
    Всегда отдаёт событие с наименьшим временем.
    """
    def __init__(self):
        self._heap = []

    def push(self, event: Event) -> None:
        """Добавить событие в календарь."""
        heapq.heappush(self._heap, event)

    def pop(self) -> Event:
        """Извлечь ближайшее событие."""
        return heapq.heappop(self._heap)

    def is_empty(self) -> bool:
        """Проверить, пуст ли календарь."""
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)