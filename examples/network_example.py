"""
Пример 4: Сеть СМО — 3 узла
frontend → backend (70%) или cache (30%)
cache → EXIT
backend → EXIT
"""
from queueing_framework.network.network import QueueingNetwork
from queueing_framework.core.node import ServiceNode, Source
from queueing_framework.distributions.distributions import Exponential
from queueing_framework.simulation.engine import SimulationEngine
from queueing_framework.metrics.performance import MetricsCalculator
from queueing_framework.visualization.plots import Visualizer


def run():
    net = QueueingNetwork()

    net.add_node(ServiceNode(
        'frontend', Exponential(10.0),
        num_servers=2,
        routing={'backend': 0.7, 'cache': 0.3}
    ))
    net.add_node(ServiceNode(
        'backend', Exponential(6.0),
        num_servers=3,
        routing={'EXIT': 1.0}
    ))
    net.add_node(ServiceNode(
        'cache', Exponential(20.0),
        num_servers=1,
        routing={'EXIT': 1.0}
    ))

    net.add_source(Source('users', 'frontend', Exponential(8.0)))
    net.validate()

    engine = SimulationEngine(net, sim_time=5000.0, warmup_time=300.0, seed=42)
    col = engine.run()
    calc = MetricsCalculator(col, 5000.0, net)

    for nid in net.node_ids():
        calc.print_report(nid)

    Visualizer.plot_network_graph(net, calc.compute_all(),
                                  save_path='network_graph.png')


if __name__ == '__main__':
    run()