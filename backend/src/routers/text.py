import os
import tempfile
import datetime
import asyncio
import concurrent.futures
from typing import Union
from fastapi import FastAPI, Response, APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from utilities import remove_files

router = APIRouter()


def process_blender(text: str) -> str:
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    # Clean default cube
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Add text
    bpy.ops.object.text_add(
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, 0),
        rotation=(3.14 * 0.5, 0, 0),
        scale=(1, 1, 1),
    )

    text_object = bpy.context.scene.objects["Text"]
    text_object.data.body = text

    text_object.data.extrude = 0.05
    text_object.data.bevel_depth = 0.01

    tmpFilePath: str = tempfile.mktemp(suffix=".glb")
    downloadFilename: str = (
        f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
    )

    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath, export_format="GLB", use_active_collection=True
    )

    return tmpFilePath


@router.get(
    "/text",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a 3D text glb (glTF binary) file.",
        }
    },
)
async def get_mdoel(
    response: Response,
    background_tasks: BackgroundTasks,
    text: str = "Untitled",
):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        tmpFilePath = await loop.run_in_executor(pool, process_blender, text)
        downloadFilename: str = (
            f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
        )

        response.headers["Content-Disposition"] = (
            f'attachment; filename="{downloadFilename}"'
        )

        background_tasks.add_task(remove_files, [tmpFilePath])
        return tmpFilePath
