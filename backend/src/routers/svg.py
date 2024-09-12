import os
import tempfile
import datetime
import asyncio
import threading
import concurrent.futures
from typing import Union
from fastapi import FastAPI, Response, APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

router = APIRouter()


def remove_file(paths: list[str]) -> None:
    for path in paths:
        os.unlink(path)


def process_blender(uploadFile: UploadFile) -> str:
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    # report the process
    # print(f"process_blender pid: {os.getpid()}")
    # print(threading.get_ident())

    # Clean default cube
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Save uploaded image
    with tempfile.NamedTemporaryFile(suffix="_" + uploadFile.filename) as uploadTmp:
        uploadTmpPath: str = uploadTmp.name
        with open(uploadTmpPath, "wb+") as out_file:
            content = uploadFile.file.read()
            out_file.write(content)

        # Impot the uploaded image
        bpy.ops.import_curve.svg(filepath=uploadTmpPath)

    for item in bpy.data.objects:
        item.data.extrude = 0.001
        item.rotation_euler = (3.14 * 0.5, 0, 0)

    # Debug, dump as blend file
    # debugTmp = tempfile.NamedTemporaryFile(suffix=".blend")
    # debugTmpPath: str = debugTmp.name
    # bpy.ops.wm.save_as_mainfile(filepath=debugTmpPath)
    # print(debugTmpPath)

    tmpFilePath: str = tempfile.mktemp(suffix=".glb")

    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath,
        export_format="GLB",
    )

    return tmpFilePath


@router.put(
    "/svg",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a glb (glTF binary) file.",
        }
    },
)
async def get_mdoel(
    response: Response, background_tasks: BackgroundTasks, uploadFile: UploadFile
):
    if uploadFile.content_type != "image/svg+xml":
        raise HTTPException(400, detail="Invalid file type")

    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        tmpFilePath = await loop.run_in_executor(pool, process_blender, uploadFile)

        downloadFilename: str = (
            f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
        )
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{downloadFilename}"'
        )

        background_tasks.add_task(remove_file, [tmpFilePath])
        return tmpFilePath
