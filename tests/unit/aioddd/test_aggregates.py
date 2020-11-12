from aioddd import AggregateRoot, Event


def test_aggregates() -> None:
    class _TestAggregateRoot(AggregateRoot):
        pass

    class _TestEvent(Event):
        pass

    agg = _TestAggregateRoot()
    evt = _TestEvent({})

    assert not len(agg.pull_aggregate_events())

    agg.record_aggregate_event(evt)
    events = agg.pull_aggregate_events()

    assert len(events) == 1
    assert not len(agg.pull_aggregate_events())
