

from fastapi import FastAPI

from biograph.api.v1.issuers import router as issuers_router
from biograph.api.v1.compounds import router as compounds_router
from biograph.api.v1.therapeutic_areas import router as tas_router
from biograph.api.v1.marketed_assets import router as marketed_assets_router


app = FastAPI()
app.include_router(issuers_router, prefix="/api/v1")
app.include_router(compounds_router, prefix="/api/v1")
app.include_router(tas_router, prefix="/api/v1")
app.include_router(marketed_assets_router, prefix="/api/v1")
