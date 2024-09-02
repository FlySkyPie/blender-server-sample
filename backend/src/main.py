from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

count: int = 0

@app.patch("/count")
def update_count():
    global count
    count += 1
    return {"count": count}


@app.get("/count")
def get_count():
    global count
    return {"count": count}
