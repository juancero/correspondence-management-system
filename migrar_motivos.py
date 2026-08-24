from database import get_connection


def migrar():
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS motivos_rendicion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo TEXT NOT NULL UNIQUE,
                activo INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        motivos_iniciales = [
            ("Entregada", "entregada"),
            ("Se mudó", "se_mudo"),
            ("Destinatario desconocido", "destinatario_desconocido"),
            ("Rechazada", "rechazada"),
            ("Domicilio insuficiente", "domicilio_insuficiente"),
            ("Fallecido", "fallecido"),
            ("Otro", "otro"),
        ]

        for nombre, codigo in motivos_iniciales:
            cur.execute("""
                INSERT OR IGNORE INTO motivos_rendicion (nombre, codigo, activo)
                VALUES (?, ?, 1)
            """, (nombre, codigo))

        conn.commit()

    print("Migración de motivos aplicada correctamente.")


if __name__ == "__main__":
    migrar()
