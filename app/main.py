"""API de exemplo (FastAPI) usada apenas para exercitar a esteira DevSecOps."""
import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# A chave vem do ambiente (nunca hardcoded). Sem ela, a API nega tudo.
# Em Kubernetes o segredo e montado como arquivo (API_KEY_FILE), nao como variavel.
_key_file = os.environ.get("API_KEY_FILE")
API_KEY = (
    Path(_key_file).read_text().strip() if _key_file else os.environ.get("API_KEY", "")
)
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="DevSecOps Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # lista explicita, sem "*"
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'"
    )
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)) -> None:
    if not API_KEY or not key or not hmac.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Nao autorizado")


class Item(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0, le=1_000_000)


ITEMS: dict[int, Item] = {}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/items/{item_id}", dependencies=[Depends(require_api_key)])
def get_item(item_id: int) -> Item:
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return item


@app.post("/items", status_code=201, dependencies=[Depends(require_api_key)])
def create_item(item: Item) -> dict:
    new_id = len(ITEMS) + 1
    ITEMS[new_id] = item
    return {"id": new_id}
