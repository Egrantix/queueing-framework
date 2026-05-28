"""
Пример 1: Одноканальная система M/M/1
λ=4, μ=5, ρ=0.8
"""
from queueing_framework.network.network import QueueingNetwork
from queueing_framework.core.node import ServiceNode, Source
from queueing_framework.distributions.distributions import Exponential
from queueing_framework.simulation.engine import SimulationEngine
from queueing_framework.metrics.performance import MetricsCalculator
from queueing_framework.visualization.plots import Visualizer


def run():
    lam, mu = 4.0, 5.0

    net = QueueingNetwork()
    net.add_node(ServiceNode(
        'server', Exponential(mu),
        num_servers=1,
        routing={'EXIT': 1.0}
    ))
    net.add_source(Source('src', 'server', Exponential(lam)))

    engine = SimulationEngine(net, sim_time=5000.0, warmup_time=200.0, seed=42)
    col = engine.run()
    calc = MetricsCalculator(col, 5000.0, net)

    calc.print_report('server')

    rho = lam / mu
    print("Аналитика M/M/1:")
    print(f"  ρ={rho:.4f}  L={rho/(1-rho):.4f}  "
          f"Lq={rho**2/(1-rho):.4f}  "
          f"W={1/(mu-lam):.4f}  "
          f"Wq={lam/(mu*(mu-lam)):.4f}")

    Visualizer.plot_queue_and_utilization(col, 'server', 'M/M/1',
                                          save_path='mm1_queue.png')
    Visualizer.plot_wait_histogram(col, 'server', 'M/M/1',
                                   save_path='mm1_hist.png')
    Visualizer.plot_network_graph(net, calc.compute_all(),
                                  save_path='mm1_graph.png')


if __name__ == '__main__':
    run()