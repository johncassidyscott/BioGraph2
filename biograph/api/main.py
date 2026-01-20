
from fastapi import FastAPI
from biograph.api.v1.issuers import router as issuers_router
from biograph.api.v1.exhibits import router as exhibits_router

app = FastAPI()
app.include_router(issuers_router, prefix="/api/v1")
app.include_router(exhibits_router, prefix="/api/v1")
