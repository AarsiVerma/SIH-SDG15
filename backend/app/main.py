from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, request_id_var
from app.core.middleware import RequestContextMiddleware
from app.core.errors import AppError, error_code_to_status
from app.schemas.common import ErrorBody

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Forest command centre for detection, correlation, risk and incident management.",
)

app.add_middleware(RequestContextMiddleware)
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(request_id=request_id_var.get()).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorBody(
            code="NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR",
            message=exc.detail,
            request_id=request_id_var.get(),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorBody(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": exc.errors()},
            request_id=request_id_var.get(),
        ).model_dump(),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorBody(
            code="CONFLICT",
            message="Database constraint violation",
            details={"detail": str(exc.orig)},
            request_id=request_id_var.get(),
        ).model_dump(),
    )


@app.get("/")
async def root() -> dict:
    return {"service": settings.app_name, "status": "ok"}