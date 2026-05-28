from collections import deque
from enum import Enum
from typing import Optional
import numpy as np


class QueueDiscipline(Enum):
    """Дисциплина обслуживания очереди."""
    FIFO = "FIFO"   # First In First Out — первый пришёл, первый ушёл
    LIFO = "LIFO"   # Last In First Out — последний пришёл, первый ушёл
    SIRO = "SIRO"   # Service In Random Order — случайный порядок


class QueueBuffer:
    """
    Буфер очереди заявок.
    Поддерживает ограниченную и неограниченную ёмкость,
    а также три дисциплины обслуживания: FIFO, LIFO, SIRO.
    """

    def __init__(
        self,
        capacity: Optional[int] = None,
        discipline: QueueDiscipline = QueueDiscipline.FIFO
    ):
        # capacity=None означает неограниченную очередь
        self.capacity = capacity
        self.discipline = discipline
        self._buffer = deque()

    def can_enqueue(self) -> bool:
        """Можно ли добавить заявку? False если очередь заполнена."""
        if self.capacity is None:
            return True
        return len(self._buffer) < self.capacity

    def enqueue(self, request) -> bool:
        """
        Добавить заявку в очередь.
        Возвращает True если успешно, False если очередь полна.
        """
        if not self.can_enqueue():
            return False
        self._buffer.append(request)
        return True

    def dequeue(self, rng: Optional[np.random.Generator] = None):
        """
        Извлечь заявку из очереди согласно дисциплине.
        rng нужен только для SIRO.
        """
        if not self._buffer:
            return None

        if self.discipline == QueueDiscipline.FIFO:
            return self._buffer.popleft()   # из начала

        if self.discipline == QueueDiscipline.LIFO:
            return self._buffer.pop()       # из конца

        if self.discipline == QueueDiscipline.SIRO:
            # случайный индекс
            idx = int(rng.integers(0, len(self._buffer)))
            request = self._buffer[idx]
            del self._buffer[idx]
            return request

    def __len__(self) -> int:
        return len(self._buffer)

    def __repr__(self) -> str:
        return (f"QueueBuffer(discipline={self.discipline.value}, "
                f"size={len(self._buffer)}, capacity={self.capacity})")