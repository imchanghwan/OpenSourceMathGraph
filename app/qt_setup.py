from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def prepare_qt_runtime() -> None:
    """Prefer PySide6 wheel DLLs over unrelated Qt DLLs on PATH."""
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    filtered_parts = [
        part
        for part in path_parts
        if not _looks_like_conda_qt_path(part)
    ]
    os.environ["PATH"] = os.pathsep.join(filtered_parts)

    spec = importlib.util.find_spec("PySide6")
    if spec is None or not spec.submodule_search_locations:
        return

    pyside_dir = Path(next(iter(spec.submodule_search_locations)))
    if pyside_dir.exists():
        os.environ["PATH"] = f"{pyside_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(pyside_dir))


def _looks_like_conda_qt_path(path_value: str) -> bool:
    normalized = path_value.lower().replace("/", "\\")
    return "\\anaconda3\\library\\" in normalized or normalized.endswith("\\anaconda3\\library\\bin")
