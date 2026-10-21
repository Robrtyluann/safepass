"""Development only. Run uv run python -m scripts.dev; binds only loopback."""

import uvicorn

from app.core.dependencies import get_identity
from app.integrations.local_identity import LocalIdentity
from app.main import create_app

app = create_app()
app.dependency_overrides[get_identity] = LocalIdentity

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
