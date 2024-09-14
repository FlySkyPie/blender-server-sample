import tempfile
import datetime
import asyncio
import concurrent.futures
from fastapi import Response, APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from utilities import remove_files

router = APIRouter()


def process_blender() -> str:
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    # report the process
    # print(f"Main pid: {os.getpid()}")
    # print(threading.get_ident())

    tmpFilePath: str = tempfile.mktemp(suffix=".glb")

    print(bpy.context.active_object)
    bpy.ops.export_scene.gltf(
        filepath=tmpFilePath, export_format="GLB", use_active_collection=True
    )

    return tmpFilePath


@router.get(
    "/test",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"model/gltf-binary": {}},
            "description": "Return a glb (glTF binary) file with Blender's default cube.",
        }
    },
    tags=["Debug"],
)
async def get_mdoel(response: Response, background_tasks: BackgroundTasks):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        tmpFilePath = await loop.run_in_executor(pool, process_blender)

        downloadFilename: str = (
            f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
        )
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{downloadFilename}"'
        )

        background_tasks.add_task(remove_files, [tmpFilePath])
        return tmpFilePath
