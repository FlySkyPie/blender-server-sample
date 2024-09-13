import tempfile
import datetime
import asyncio
import concurrent.futures
import math
from scipy.spatial.transform import Rotation as R

from fastapi import Response, APIRouter, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from utilities import remove_files

router = APIRouter()


def process_blender(polar_angle: float, azimuth_angle: float) -> str:
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy

    # report the process
    # print(f"Main pid: {os.getpid()}")
    # print(threading.get_ident())

    bpy.ops.wm.open_mainfile(filepath="assets/blenders/24-v-power-supply.blend")
    camera = bpy.context.scene.camera

    rotation = R.from_euler("xzy", [-polar_angle, azimuth_angle, 0], degrees=True)
    [x, y, z] = rotation.apply([0, -1, 0])
    camera.location.x = x
    camera.location.y = y
    camera.location.z = z

    camera_rotation = R.from_euler(
        "XZY",
        [
            90 - polar_angle,
            0,
            azimuth_angle,
        ],
        degrees=True,
    )
    camera.rotation_mode = "XZY"
    camera.rotation_euler = camera_rotation.as_euler("XZY", degrees=False)

    tmpFilePath: str = tempfile.mktemp(suffix=".png")

    bpy.context.scene.render.filepath = tmpFilePath
    # bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    # bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
    # bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.render.resolution_x = 720
    bpy.context.scene.render.resolution_y = 480
    result = bpy.ops.render.render(write_still=True)

    return tmpFilePath


@router.get(
    "/render/sample-1",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Return a image of power supply rendered by Blender",
        }
    },
)
async def render_from_file(
    response: Response,
    background_tasks: BackgroundTasks,
    polar_angle: float = Query(default=0, ge=-90, le=90),
    azimuth_angle: float = 0,
):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        tmpFilePath = await loop.run_in_executor(
            pool, process_blender, polar_angle, azimuth_angle
        )

        # downloadFilename: str = (
        #     f"{datetime.datetime.now().replace(microsecond=0).isoformat()}.glb"
        # )
        # response.headers["Content-Disposition"] = (
        #     f'attachment; filename="{downloadFilename}"'
        # )

        background_tasks.add_task(remove_files, [tmpFilePath])
        return tmpFilePath
