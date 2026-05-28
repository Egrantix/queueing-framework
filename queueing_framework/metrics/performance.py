import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from queueing_framework.statistics.collector import StatisticsCollector
from queueing_framework.network.network import QueueingNetwork


@dataclass
class NodeMetrics:
    """
    Результаты расчёта характеристик одного узла СМО.
    Все метрики рассчитываются по данным имитации.
    """
    node_id: str

    L: float       # среднее число заявок в системе
    Lq: float      # среднее число заявок в очереди
    W: float       # среднее время пребывания в системе
    Wq: float      # среднее время ожидания в очереди
    rho: float     # коэффициент загрузки серверов
    P_loss: float  # вероятность отказа
    X: float       # пропускная способность (заявок в ед. времени)

    arrivals: int  # число поступивших заявок
    served: int    # число обслуженных заявок
    dropped: int   # число потерянных заявок


class MetricsCalculator:
    """
    Рассчитывает характеристики СМО по данным сборщика статистики.
    Использует метод площадей для L и Lq,
    выборочные средние для W и Wq.
    """

    def __init__(
        self,
        collector: StatisticsCollector,
        sim_end: float,
        network: QueueingNetwork
    ):
        self.c = collector
        self.sim_end = sim_end
        self.network = network
        # длительность наблюдения (после прогрева)
        self.obs_time = sim_end - collector._stats_start_time

    def _time_average(
        self,
        history: List[Tuple[float, int]],
        t_start: float,
        t_end: float
    ) -> float:
        """
        Рассчитать среднее значение кусочно-постоянного процесса
        методом площадей (интеграл / длительность).

        history — список пар (время, значение).
        Считаем площадь под ступенчатым графиком от t_start до t_end.
        """
        if not history:
            return 0.0

        # берём только точки до t_end
        points = [(t, v) for t, v in history if t <= t_end]
        if not points:
            return 0.0

        total_area = 0.0

        for i in range(len(points) - 1):
            t0, v0 = points[i]
            t1, _  = points[i + 1]
            # пересечение с окном наблюдения [t_start, t_end]
            seg_start = max(t0, t_start)
            seg_end   = min(t1, t_end)
            if seg_end > seg_start:
                total_area += v0 * (seg_end - seg_start)

        # последний отрезок — от последней точки до t_end
        t_last, v_last = points[-1]
        seg_start = max(t_last, t_start)
        if t_end > seg_start:
            total_area += v_last * (t_end - seg_start)

        duration = t_end - t_start
        return total_area / duration if duration > 0 else 0.0

    def compute(self, node_id: str) -> NodeMetrics:
        """Рассчитать все метрики для одного узла."""
        c = self.c
        node = self.network.nodes[node_id]
        t0 = c._stats_start_time
        te = self.sim_end

        # Lq — среднее число заявок в очереди (метод площадей)
        Lq = self._time_average(c.queue_length_history[node_id], t0, te)

        # среднее число занятых серверов (метод площадей)
        avg_busy = self._time_average(c.busy_servers_history[node_id], t0, te)

        # L = Lq + среднее число занятых серверов
        L = Lq + avg_busy

        # Wq и W — выборочные средние по всем обслуженным заявкам
        wt = c.wait_times[node_id]
        st = c.sojourn_times[node_id]
        Wq = float(np.mean(wt)) if wt else 0.0
        W  = float(np.mean(st)) if st else 0.0

        # ρ — загрузка: суммарное время занятости / (число серверов × время наблюдения)
        num_servers = node.num_servers if node.num_servers is not None else max(1, c.served[node_id])
        rho = min(c.busy_time[node_id] / (num_servers * self.obs_time), 1.0) \
              if self.obs_time > 0 else 0.0

        # X — пропускная способность
        X = c.served[node_id] / self.obs_time if self.obs_time > 0 else 0.0

        # P_loss — вероятность отказа
        total = c.arrivals[node_id]
        P_loss = c.dropped[node_id] / total if total > 0 else 0.0

        return NodeMetrics(
            node_id=node_id,
            L=L, Lq=Lq, W=W, Wq=Wq,
            rho=rho, P_loss=P_loss, X=X,
            arrivals=total,
            served=c.served[node_id],
            dropped=c.dropped[node_id]
        )

    def compute_all(self) -> Dict[str, NodeMetrics]:
        """Рассчитать метрики для всех узлов сети."""
        return {nid: self.compute(nid) for nid in self.c.node_ids}

    def print_report(self, node_id: Optional[str] = None) -> None:
        """Вывести таблицу метрик в терминал."""
        nodes = [node_id] if node_id else self.c.node_ids
        print(f"\n{'='*55}")
        for nid in nodes:
            m = self.compute(nid)
            print(f"  Узел: {nid}")
            print(f"  {'-'*45}")
            print(f"  {'Метрика':<20} {'Значение':>12}")
            print(f"  {'-'*45}")
            print(f"  {'ρ (загрузка)':<20} {m.rho:>12.4f}")
            print(f"  {'L (в системе)':<20} {m.L:>12.4f}")
            print(f"  {'Lq (в очереди)':<20} {m.Lq:>12.4f}")
            print(f"  {'W (пребывание)':<20} {m.W:>12.4f}")
            print(f"  {'Wq (ожидание)':<20} {m.Wq:>12.4f}")
            print(f"  {'X (пропускн.)':<20} {m.X:>12.4f}")
            print(f"  {'P_loss (отказ)':<20} {m.P_loss:>12.4f}")
            print(f"  {'-'*45}")
            print(f"  Поступило: {m.arrivals}  |  Обслужено: {m.served}  |  Потеряно: {m.dropped}")
        print(f"{'='*55}\n")