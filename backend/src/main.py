import os
import tempfile
import datetime
from typing import Union
from multiprocessing import current_process
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

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


def remove_file(path: str) -> None:
    os.unlink(path)


@app.get(
    "/model",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a glb (glTF binary) file.",
        }
    },)
def get_mdoel(response: Response, background_tasks: BackgroundTasks):
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    tmp = tempfile.NamedTemporaryFile(suffix='.glb')
    tmpFilePath: str = tmp.name
    downloadFilename: str = f'{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb'

    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath,
        export_format='GLB',
        use_active_collection=True
    )

    response.headers["Content-Disposition"] = f'attachment; filename="{downloadFilename}"'

    background_tasks.add_task(remove_file, tmpFilePath)
    return tmpFilePath
