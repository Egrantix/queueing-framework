import numpy as np
from typing import Callable
class Distribution:
    """Базовый класс для всех законов распределения."""
    def sample(self, rng: np.random.Generator) -> float:
        raise NotImplementedError
class Exponential(Distribution):
    """Экспоненциальное распределение. rate = интенсивность потока."""
    def __init__(self, rate: float):
        self.rate = rate

    def sample(self, rng: np.random.Generator) -> float:
        return rng.exponential(1.0 / self.rate)
class Deterministic(Distribution):
    """Постоянное значение — время всегда одинаково."""
    def __init__(self, value: float):
        self.value = value

    def sample(self, rng: np.random.Generator) -> float:
        return self.value
class Uniform(Distribution):
    """Равномерное распределение на отрезке [low, high]."""
    def __init__(self, low: float, high: float):
        self.low = low
        self.high = high

    def sample(self, rng: np.random.Generator) -> float:
        return rng.uniform(self.low, self.high)
class Normal(Distribution):
    """Нормальное распределение. Отрицательные значения обрезаются до 0."""
    def __init__(self, mean: float, std: float):
        self.mean = mean
        self.std = std

    def sample(self, rng: np.random.Generator) -> float:
        return max(0.0, rng.normal(self.mean, self.std))
class Erlang(Distribution):
    """Распределение Эрланга: сумма k экспоненциальных с параметром rate."""
    def __init__(self, k: int, rate: float):
        self.k = k
        self.rate = rate

    def sample(self, rng: np.random.Generator) -> float:
        return rng.gamma(self.k, 1.0 / self.rate)
class Weibull(Distribution):
    """Распределение Вейбулла."""
    def __init__(self, shape: float, scale: float):
        self.shape = shape
        self.scale = scale

    def sample(self, rng: np.random.Generator) -> float:
        return self.scale * rng.weibull(self.shape)
class CustomDistribution(Distribution):
    """Произвольный закон через пользовательскую функцию."""
    def __init__(self, func: Callable[[np.random.Generator], float]):
        self.func = func

    def sample(self, rng: np.random.Generator) -> float:
        return self.func(rng)