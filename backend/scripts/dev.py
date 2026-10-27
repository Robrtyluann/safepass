"""Development only. Run uv run python -m scripts.dev; binds only loopback."""

import uvicorn

from app.core.dependencies import get_identity, get_provider_catalog
from app.integrations.local_identity import LocalIdentity
from app.integrations.local_provider_catalog import LocalProviderCatalog
from app.main import create_app

app = create_app()
app.dependency_overrides[get_identity] = LocalIdentity
app.dependency_overrides[get_provider_catalog] = LocalProviderCatalog

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
