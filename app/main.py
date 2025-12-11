import logging
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, schemas
from app.database import engine
from app.routers import post, auth
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Settings for logging
logging.basicConfig(level=logging.INFO)

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url.path} {response.status_code} {process_time:.2f}s")
    return response

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {'message': "Hello World"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.ErrorDetail(
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
            status=exc.status_code
        ).model_dump()
    )
