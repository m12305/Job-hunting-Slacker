from pathlib import Path
import sys


backend_dir = Path(SPECPATH)
project_root = backend_dir.parent

datas = [
    (str(backend_dir / "alembic"), "alembic"),
    (str(backend_dir / "alembic.ini"), "."),
    (str(project_root / "fronted" / "dist"), "web"),
]

# Conda keeps a few CPython runtime dependencies in Library/bin, outside the
# locations PyInstaller scans automatically. The files do not exist in the
# standard python.org runtime used by GitHub Actions, so include them only when
# building from a Conda environment.
conda_bin = Path(sys.prefix) / "Library" / "bin"
binaries = [
    (str(dll_path), ".")
    for dll_name in ("ffi.dll", "sqlite3.dll")
    if (dll_path := conda_bin / dll_name).is_file()
]

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan.on",
]

a = Analysis(
    [str(backend_dir / "desktop_entry.py")],
    pathex=[str(backend_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="qiuzhao-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="qiuzhao-backend",
)
