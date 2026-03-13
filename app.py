import os
import secrets
import io

from fastapi import FastAPI, UploadFile, File, Query, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader

from fixture import generate_fixtures

API_KEY = os.environ.get("API_KEY", "changeme")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI(title="Fixture Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_methods=["POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


async def verify_api_key(key: str = Security(api_key_header)):
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.post("/generate", dependencies=[Depends(verify_api_key)])
async def generate(
    file: UploadFile = File(...),
    num_teams: int = Query(4, ge=2),
    min_groups: int = Query(10, ge=1),
):
    contents = await file.read()
    output_bytes = generate_fixtures(contents, num_teams=num_teams, min_groups=min_groups)

    return StreamingResponse(
        io.BytesIO(output_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Fixtures.xlsx"},
    )
