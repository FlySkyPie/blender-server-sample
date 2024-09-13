import os
import tempfile
import datetime
from typing import Union
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from routers import text, test, svg, render, render_sample_1

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=text.router, prefix="/api/v1")
app.include_router(router=test.router, prefix="/api/v1")
app.include_router(router=svg.router, prefix="/api/v1")
app.include_router(router=render.router, prefix="/api/v1")
app.include_router(router=render_sample_1.router, prefix="/api/v1")
