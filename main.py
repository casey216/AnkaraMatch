from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.core.database import Base, engine
from api.v1.auth.route import auth
from api.v1.core.settings import settings
from api.v1.core.middleware import LoggingMiddleware

app = FastAPI()
app.include_router(auth, prefix=settings.API_PREFIX)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

@app.on_event("startup")
def startup():
    from api.v1.core.database import Base, engine
    from api.v1.auth.model import User
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)


@app.get("/healthcheck")
async def health_check():
    """Checks if server is active."""
    return {"status": "active"}
