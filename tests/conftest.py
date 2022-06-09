import sys
from asyncio import AbstractEventLoop, get_event_loop_policy
from unittest.mock import MagicMock

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:

    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)


from _pytest.main import Session
from pytest import fixture


def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    # --suppress-no-test-exit-code
    if exitstatus == 5:
        session.exitstatus = 0


@fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    return get_event_loop_policy().new_event_loop()
