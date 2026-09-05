import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.api.v1.endpoints import auth, deals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_logging(request: Request, call_next):
    """لاگ‌گیری ساده + هدر زمان پردازش، برای مانیتورینگ پرفورمنس"""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    logger.info(f"{request.method} {request.url.path} - {duration_ms:.2f}ms")
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """خطاهای اعتبارسنجی رو به فرمت یکدست و خواناتر برمی‌گردونه"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "خطای اعتبارسنجی ورودی", "errors": exc.errors()},
    )


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(deals.router, prefix=settings.API_V1_PREFIX)
# سایر روترها (contacts, companies, activities, pipelines, reports) به همین ترتیب اضافه می‌شن
