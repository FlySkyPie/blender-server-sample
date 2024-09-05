import tempfile
from typing import Union
from multiprocessing import current_process
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


@app.get("/model")
def get_mdoel():
    # Used to fix `ModuleNotFoundError: No module named '_bpy'` issue.
    import bpy
    with tempfile.NamedTemporaryFile() as tmp:

        print(f'{tmp.name}.glb')
        bpy.ops.export_scene.gltf(
            filepath=f'{tmp.name}.glb',
            export_format='GLB',
            use_active_collection=True
        )

    return {"count": 0}
