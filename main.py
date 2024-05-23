
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.middleware.redis_cache import clear_cache
from app.routers.leaderboard import router


app = FastAPI(
    title='gokz.top',
    description='GOKZ TOP Leaderboard API',
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_cache, CronTrigger(hour=8, minute=0))
    scheduler.start()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
