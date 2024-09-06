import tempfile
import datetime
from typing import Union
from multiprocessing import current_process
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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


@app.get(
    "/model",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a glb (glTF binary) file.",
        }
    },)
def get_mdoel(response: Response):
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    tmp = tempfile.NamedTemporaryFile()
    tmpFilePath = f'{tmp.name}.glb'
    downloadFilename = f'{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb'

    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath,
        export_format='GLB',
        use_active_collection=True
    )

    response.headers["Content-Disposition"] = f'attachment; filename="{downloadFilename}"'

    return tmpFilePath
