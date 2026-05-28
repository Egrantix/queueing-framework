from typing import Dict, Optional
from queueing_framework.core.node import ServiceNode, Source


class QueueingNetwork:
    """
    Сеть систем массового обслуживания.
    Хранит узлы и источники заявок, описывает топологию сети.
    """

    def __init__(self):
        # словарь узлов: node_id -> ServiceNode
        self.nodes: Dict[str, ServiceNode] = {}

        # словарь источников: source_id -> Source
        self.sources: Dict[str, Source] = {}

    def add_node(self, node: ServiceNode) -> None:
        """Добавить узел в сеть."""
        self.nodes[node.node_id] = node

    def add_source(self, source: Source) -> None:
        """Добавить источник заявок."""
        self.sources[source.source_id] = source

    def get_node(self, node_id: str) -> ServiceNode:
        """Получить узел по идентификатору."""
        if node_id not in self.nodes:
            raise KeyError(f"Узел '{node_id}' не найден в сети.")
        return self.nodes[node_id]

    def node_ids(self):
        """Список идентификаторов всех узлов."""
        return list(self.nodes.keys())

    def validate(self) -> None:
        """
        Проверить корректность сети:
        - все узлы в маршрутах существуют
        - вероятности маршрутов суммируются в 1.0
        """
        for node in self.nodes.values():
            total_prob = 0.0
            for dest, prob in node.routing.items():
                total_prob += prob
                if dest != "EXIT" and dest not in self.nodes:
                    raise ValueError(
                        f"Узел '{dest}' в маршруте '{node.node_id}' "
                        f"не существует в сети."
                    )
            if node.routing and abs(total_prob - 1.0) > 1e-9:
                raise ValueError(
                    f"Сумма вероятностей маршрутов узла '{node.node_id}' "
                    f"= {total_prob:.4f}, должна быть 1.0"
                )

    def __repr__(self) -> str:
        return (f"QueueingNetwork("
                f"nodes={list(self.nodes.keys())}, "
                f"sources={list(self.sources.keys())})")