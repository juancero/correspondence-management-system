import shutil
from datetime import datetime
from pathlib import Path

from database import DB_PATH


def crear_backup():
    base_dir = Path(__file__).resolve().parent.parent
    backup_dir = base_dir / "backups"
    backup_dir.mkdir(exist_ok=True)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = backup_dir / f"backup_{fecha}.db"

    shutil.copy2(DB_PATH, destino)

    return destino
