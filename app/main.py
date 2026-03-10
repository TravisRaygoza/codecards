from app.api.routers.user import router as user_router
from app.api.routers.deck import router as deck_router
from app.api.routers.card import router as card_router
from app.api.routers.study import router as study_router
from app.api.routers.ai import router as ai_router
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.database.session import create_db_tables
from app.config import app_settings
 

async def lifespan_handler(app:FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler, title=app_settings.APP_NAME)
app.include_router(user_router)
app.include_router(deck_router)
app.include_router(card_router)
app.include_router(study_router)
app.include_router(ai_router)


@app.get("/")
def read_root():
    return {"detail": "Server is running..."}





@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
