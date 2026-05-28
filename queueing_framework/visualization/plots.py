import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Optional, Dict
from queueing_framework.statistics.collector import StatisticsCollector
from queueing_framework.metrics.performance import NodeMetrics
from queueing_framework.network.network import QueueingNetwork


class Visualizer:
    """
    Визуализация результатов моделирования.
    Строит графики очередей, загрузки серверов,
    гистограммы ожидания и граф сети.
    """

    @staticmethod
    def plot_queue_and_utilization(
        collector: StatisticsCollector,
        node_id: str,
        title: str = "",
        save_path: Optional[str] = None
    ) -> None:
        """
        График длины очереди и занятости серверов во времени.
        Два подграфика: верхний — очередь, нижний — серверы.
        """
        qh = collector.queue_length_history[node_id]
        bh = collector.busy_servers_history[node_id]

        if not qh:
            print(f"Нет данных для узла '{node_id}'")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        fig.suptitle(f"{title}  |  узел: {node_id}", fontsize=13)

        # --- верхний график: длина очереди ---
        tq = [t for t, _ in qh]
        vq = [v for _, v in qh]
        ax1.step(tq, vq, where='post', color='steelblue', linewidth=1.2)
        ax1.fill_between(tq, vq, step='post', alpha=0.2, color='steelblue')
        ax1.set_ylabel("Длина очереди", fontsize=11)
        ax1.grid(True, alpha=0.3)

        # --- нижний график: занятые серверы ---
        tb = [t for t, _ in bh]
        vb = [v for _, v in bh]
        ax2.step(tb, vb, where='post', color='darkorange', linewidth=1.2)
        ax2.fill_between(tb, vb, step='post', alpha=0.2, color='darkorange')
        ax2.set_ylabel("Занято серверов", fontsize=11)
        ax2.set_xlabel("Модельное время", fontsize=11)
        ax2.grid(True, alpha=0.3)

        # отметить конец прогрева вертикальной линией
        if collector.warmup_time > 0:
            ax1.axvline(
                collector.warmup_time, color='red',
                linestyle='--', alpha=0.7, label='Конец прогрева'
            )
            ax2.axvline(
                collector.warmup_time, color='red',
                linestyle='--', alpha=0.7
            )
            ax1.legend(fontsize=9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=120, bbox_inches='tight')
            print(f"График сохранён: {save_path}")
        else:
            plt.show()
        plt.close()

    @staticmethod
    def plot_wait_histogram(
        collector: StatisticsCollector,
        node_id: str,
        title: str = "",
        save_path: Optional[str] = None
    ) -> None:
        """
        Гистограмма времени ожидания в очереди.
        """
        wt = collector.wait_times[node_id]
        if not wt:
            print(f"Нет данных ожидания для узла '{node_id}'")
            return

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.hist(wt, bins=50, color='mediumseagreen', edgecolor='white', alpha=0.85)
        ax.axvline(
            np.mean(wt), color='red', linestyle='--', linewidth=1.5,
            label=f'Среднее Wq = {np.mean(wt):.4f}'
        )
        ax.set_xlabel("Время ожидания", fontsize=11)
        ax.set_ylabel("Число заявок", fontsize=11)
        ax.set_title(f"{title}  |  гистограмма ожидания ({node_id})", fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=120, bbox_inches='tight')
            print(f"График сохранён: {save_path}")
        else:
            plt.show()
        plt.close()

    @staticmethod
    def plot_network_graph(
        network: QueueingNetwork,
        metrics: Optional[Dict[str, NodeMetrics]] = None,
        save_path: Optional[str] = None
    ) -> None:
        """
        Граф топологии сети СМО.
        Узлы — прямоугольники с метриками, рёбра — маршруты с вероятностями.
        """
        G = nx.DiGraph()

        # добавляем узлы сети
        for nid in network.nodes:
            G.add_node(nid)

        # добавляем рёбра из маршрутов
        for nid, node in network.nodes.items():
            for dest, prob in node.routing.items():
                if dest != "EXIT":
                    G.add_edge(nid, dest, weight=prob)

        # добавляем источники как отдельные узлы
        source_nodes = []
        for src in network.sources.values():
            src_label = f"[SRC]\n{src.source_id}"
            G.add_node(src_label)
            G.add_edge(src_label, src.target_node_id)
            source_nodes.append(src_label)

        fig, ax = plt.subplots(figsize=(11, 6))

        pos = nx.spring_layout(G, seed=1, k=2.5)

        # цвета: источники — серые, узлы СМО — синие
        node_colors = [
            'lightgray' if n in source_nodes else 'steelblue'
            for n in G.nodes()
        ]

        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors,
            node_size=2200, ax=ax, alpha=0.9
        )
        nx.draw_networkx_labels(
            G, pos, font_size=8,
            font_color='white', ax=ax
        )
        nx.draw_networkx_edges(
            G, pos, ax=ax, arrows=True,
            arrowsize=20, edge_color='gray',
            width=1.8, connectionstyle='arc3,rad=0.08'
        )

        # подписи вероятностей на рёбрах
        edge_labels = {
            (u, v): f"{d['weight']:.2f}"
            for u, v, d in G.edges(data=True)
            if 'weight' in d
        }
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels, font_size=8, ax=ax
        )

        # подписи метрик под каждым узлом
        if metrics:
            for nid, m in metrics.items():
                if nid in pos:
                    x, y = pos[nid]
                    ax.text(
                        x, y - 0.22,
                        f"ρ={m.rho:.2f}  Lq={m.Lq:.2f}",
                        ha='center', fontsize=8,
                        bbox=dict(
                            boxstyle='round,pad=0.3',
                            facecolor='lightyellow',
                            alpha=0.85
                        )
                    )

        ax.set_title("Топология сети СМО", fontsize=13)
        ax.axis('off')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=120, bbox_inches='tight')
            print(f"График сохранён: {save_path}")
        else:
            plt.show()
        plt.close()