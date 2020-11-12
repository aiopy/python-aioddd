from abc import ABC
from typing import List

from .events import Event


class Aggregate(ABC):
    pass


class AggregateRoot(Aggregate):
    _events: List[Event]

    def __init__(self) -> None:
        self._events = []

    def pull_aggregate_events(self) -> List[Event]:
        _events = self._events
        self._events = []
        return _events

    def record_aggregate_event(self, event: Event) -> None:
        self._events.append(event)
