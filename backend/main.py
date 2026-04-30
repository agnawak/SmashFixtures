import io
import secrets

from fastapi import Depends, FastAPI, File, HTTPException, Query, Security, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from backend.config import ALLOWED_ORIGINS, APP_PASSWORD, APP_USERNAME, LEGACY_API_KEY
from backend.database import Base, SessionLocal, engine, get_db
from backend.models import User
from backend.schemas import AuthRequest, AuthResponse, SignupResponse
from backend.security import generate_api_key, hash_password, verify_password
from fixture import generate_custom_fixtures, generate_fixtures

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(title="Fixture Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

    # Optional bootstrap user for first-time deployments.
    if APP_USERNAME and APP_PASSWORD:
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.username == APP_USERNAME).first()
            if not existing:
                db_user = User(
                    username=APP_USERNAME,
                    password_hash=hash_password(APP_PASSWORD),
                    api_key=generate_api_key(),
                    is_active=True,
                )
                db.add(db_user)
                db.commit()
        finally:
            db.close()


async def verify_api_key(
    key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> User | None:
    if not key:
        raise HTTPException(status_code=403, detail="Missing API key")

    user = db.query(User).filter(User.api_key == key, User.is_active.is_(True)).first()
    if user:
        return user

    # Temporary fallback for legacy integrations using a single static API key.
    if LEGACY_API_KEY and secrets.compare_digest(key, LEGACY_API_KEY):
        return None

    raise HTTPException(status_code=403, detail="Invalid API key")


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/signup", response_model=SignupResponse)
def signup(body: AuthRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    db_user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        api_key=generate_api_key(),
        is_active=True,
    )
    db.add(db_user)
    db.commit()

    return {
        "message": "Signup successful",
        "api_key": db_user.api_key,
        "username": db_user.username,
    }


@app.post("/login", response_model=AuthResponse)
def login(body: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username, User.is_active.is_(True)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"api_key": user.api_key, "username": user.username}


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


@app.post("/generate-custom", dependencies=[Depends(verify_api_key)])
async def generate_custom(
    file: UploadFile = File(...),
    players_per_team: int = Query(7, ge=2),
    min_groups: int = Query(10, ge=1),
    use_setters: bool = Query(True),
    use_tierlists: bool = Query(True),
):
    contents = await file.read()
    try:
        output_bytes = generate_custom_fixtures(
            contents,
            players_per_team=players_per_team,
            min_groups=min_groups,
            use_setters=use_setters,
            use_tierlists=use_tierlists,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(
        io.BytesIO(output_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=CustomFixtures.xlsx"},
    )
