from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class Request:
    """
    Заявка в системе массового обслуживания.
    Хранит полную историю прохождения по сети.
    """
    request_id: int
    created_at: float

    arrival_times: Dict[str, float] = field(default_factory=dict)
    service_start_times: Dict[str, float] = field(default_factory=dict)
    service_end_times: Dict[str, float] = field(default_factory=dict)

    departure_time: Optional[float] = None
    route: List[str] = field(default_factory=list)

    dropped: bool = False
    dropped_at_node: Optional[str] = None

    attributes: Dict[str, Any] = field(default_factory=dict)

    def wait_time(self, node_id: str) -> Optional[float]:
        """Время ожидания в очереди = начало обслуживания - момент прихода."""
        if node_id in self.service_start_times and node_id in self.arrival_times:
            return self.service_start_times[node_id] - self.arrival_times[node_id]
        return None

    def sojourn_time(self, node_id: str) -> Optional[float]:
        """Полное время пребывания в узле = конец обслуживания - момент прихода."""
        if node_id in self.service_end_times and node_id in self.arrival_times:
            return self.service_end_times[node_id] - self.arrival_times[node_id]
        return None