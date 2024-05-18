from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html

from app.routers.leaderboard import router

app = FastAPI(
    docs_url=None,
    title='gokz.top',
)
app.include_router(router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
    )


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

