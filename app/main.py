from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, schemas
from app.database import engine
from app.routers import post, auth
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
