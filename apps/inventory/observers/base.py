from abc import ABC, abstractmethod
from typing import List


class StockObserver(ABC):
    @abstractmethod
    def update(self, *, product, movement) -> None:
        ...


class StockSubject:
    def __init__(self) -> None:
        self._observers: List[StockObserver] = []

    def attach(self, observer: StockObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: StockObserver) -> None:
        self._observers.remove(observer)

    def notify(self, *, product, movement) -> None:
        for observer in self._observers:
            observer.update(product=product, movement=movement)

