import os

def remove_files(paths: list[str]) -> None:
    for path in paths:
        os.unlink(path)
