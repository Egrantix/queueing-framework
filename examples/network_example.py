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
import time
from pprint import pprint

def run():
    net = QueueingNetwork()
    st = time.time()
    net.add_node(ServiceNode(
        'frontend', Exponential(120.0),
        num_servers=2,
        routing={'backend': 0.7, 'cache': 0.3}
    ))
    net.add_node(ServiceNode(
        'backend', Exponential(60.0),
        num_servers=3,
        routing={'EXIT': 1.0}
    ))
    net.add_node(ServiceNode(
        'cache', Exponential(200.0),
        num_servers=1,
        routing={'EXIT': 1.0}
    ))

    net.add_source(Source('users', ['frontend'], Exponential(80.0)))
    net.validate()
    print(net)
    
    
    engine = SimulationEngine(net, sim_time=2000.0, warmup_time=20.0, seed=42)
    col = engine.run(2000.0)
    
    calc = MetricsCalculator(col, 2000.0, net)
 
    for nid in net.node_ids():
        calc.print_report(nid)
    
    Visualizer.plot_network_graph(net, calc.compute_all(),
                                  save_path='network_graph.png')


if __name__ == '__main__':
    run()