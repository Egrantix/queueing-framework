"""
Пример 3: Система с ограниченной ёмкостью M/M/1/K
λ=6, μ=5, K=5 (система вмещает не более 5 заявок)
Ожидаем ненулевую вероятность отказа P_loss
"""
from queueing_framework.network.network import QueueingNetwork
from queueing_framework.core.node import ServiceNode, Source
from queueing_framework.distributions.distributions import Exponential
from queueing_framework.simulation.engine import SimulationEngine
from queueing_framework.metrics.performance import MetricsCalculator


def run():
    lam, mu, K = 6.0, 5.0, 5

    net = QueueingNetwork()
    net.add_node(ServiceNode(
        'server', Exponential(mu),
        num_servers=1,
        system_capacity=K,
        routing={'EXIT': 1.0}
    ))
    net.add_source(Source('src', 'server', Exponential(lam)))

    engine = SimulationEngine(net, sim_time=5000.0, warmup_time=200.0, seed=42)
    col = engine.run()
    calc = MetricsCalculator(col, 5000.0, net)

    calc.print_report('server')

    # аналитическая P_loss для M/M/1/K
    rho = lam / mu
    p0 = (1 - rho) / (1 - rho**(K+1))
    p_loss = p0 * rho**K
    print(f"Аналитика M/M/1/{K}: P_loss={p_loss:.4f}  ρ={rho:.4f}")


if __name__ == '__main__':
    run()