import os
import tempfile
import datetime
import threading
from typing import Union
from fastapi import FastAPI, Response, APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

router = APIRouter()


def remove_file(path: str) -> None:
    os.unlink(path)


@router.get(
    "/test",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a glb (glTF binary) file with Blender's default cube.",
        }
    },
)
def get_mdoel(response: Response, background_tasks: BackgroundTasks):
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    # report the process
    print(f'Main pid: {os.getpid()}')
    print(threading.get_ident())

    tmpFilePath: str = tempfile.mktemp(suffix=".glb")
    downloadFilename: str = (
        f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
    )

    print(bpy.context.active_object)
    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath, export_format="GLB", use_active_collection=True
    )

    response.headers["Content-Disposition"] = (
        f'attachment; filename="{downloadFilename}"'
    )

    background_tasks.add_task(remove_file, tmpFilePath)
    return tmpFilePath
