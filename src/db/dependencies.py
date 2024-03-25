import contextlib
from collections.abc import AsyncIterator

from motor.core import AgnosticClientSession

from .client import client


@contextlib.asynccontextmanager
async def create_session() -> AsyncIterator[AgnosticClientSession]:
    async with await client.start_session() as session:
        yield session
