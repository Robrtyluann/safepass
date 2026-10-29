from datetime import UTC, datetime

import pytest

from app.core.rate_limit import limiter


class FixedClock:
    def __init__(self, now: datetime | None = None) -> None:
        self._now = now or datetime(2026, 11, 1, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta) -> None:  # type: ignore[no-untyped-def]
        self._now += delta


class FakeUow:
    def __init__(self) -> None:
        self.commits = 0
        self.flushes = 0

    def commit(self) -> None:
        self.commits += 1

    def flush(self) -> None:
        self.flushes += 1


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def uow() -> FakeUow:
    return FakeUow()


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    limiter.reset()
