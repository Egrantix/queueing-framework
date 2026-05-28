"""
Пример 2: Многоканальная система M/M/n
λ=8, μ=5, n=3, ρ=λ/(n·μ)=0.533
"""
from queueing_framework.network.network import QueueingNetwork
from queueing_framework.core.node import ServiceNode, Source
from queueing_framework.distributions.distributions import Exponential
from queueing_framework.simulation.engine import SimulationEngine
from queueing_framework.metrics.performance import MetricsCalculator


def run():
    lam, mu, n = 8.0, 5.0, 3

    net = QueueingNetwork()
    net.add_node(ServiceNode(
        'servers', Exponential(mu),
        num_servers=n,
        routing={'EXIT': 1.0}
    ))
    net.add_source(Source('src', 'servers', Exponential(lam)))

    engine = SimulationEngine(net, sim_time=5000.0, warmup_time=200.0, seed=42)
    col = engine.run()
    calc = MetricsCalculator(col, 5000.0, net)

    calc.print_report('servers')
    rho = lam / (n * mu)
    print(f"Аналитика M/M/{n}: ρ={rho:.4f}")


if __name__ == '__main__':
    run()