
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routers.leaderboard import router

app = FastAPI(
    title='gokz.top',
    description='GOKZ TOP Leaderboard API',
)

app.add_middleware(
    CORSMiddleware,  # NOQA
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
