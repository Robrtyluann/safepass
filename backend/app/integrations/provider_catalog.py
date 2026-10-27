"""Port for the provider catalog owned by Desafio 03 / squad-47.

Squad-47's `providers` module is not merged into this branch. Marketplace and
reviews depend on provider identity and summary data but never create a
`providers` table here, to avoid a second, diverging source of truth. Swap
`UnconfiguredProviderCatalog` for a real HTTP or in-process adapter once that
module lands in `main`.
"""

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.exceptions import unavailable


class ProviderSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    name: str = Field(max_length=160)
    category: str = Field(max_length=160)
    tags: list[str] = Field(default_factory=list)
    price_tier: str = Field(pattern=r"^(baixo|medio|alto)$")
    image_url: str | None = None
    contact: str | None = None


class ProviderCatalogGateway(Protocol):
    def search(
        self,
        query: str,
        category: str | None,
        price_tier: str | None,
        tags: list[str],
        page: int,
        size: int,
    ) -> tuple[list[ProviderSummary], int]: ...

    def get(self, provider_id: UUID) -> ProviderSummary | None: ...


class UnconfiguredProviderCatalog:
    """Fail closed; never substitute fabricated providers in production."""

    def search(
        self,
        query: str,
        category: str | None,
        price_tier: str | None,
        tags: list[str],
        page: int,
        size: int,
    ) -> tuple[list[ProviderSummary], int]:
        raise unavailable()

    def get(self, provider_id: UUID) -> ProviderSummary | None:
        raise unavailable()
