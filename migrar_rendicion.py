from database import get_connection


def columna_existe(cursor, tabla, columna):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [row["name"] for row in cursor.fetchall()]
    return columna in columnas


def migrar():
    with get_connection() as conn:
        cur = conn.cursor()

        if not columna_existe(cur, "correspondencias", "resultado_rendicion"):
            cur.execute("ALTER TABLE correspondencias ADD COLUMN resultado_rendicion TEXT")

        if not columna_existe(cur, "correspondencias", "fecha_rendicion"):
            cur.execute("ALTER TABLE correspondencias ADD COLUMN fecha_rendicion TEXT")

        if not columna_existe(cur, "correspondencias", "numero_rendicion"):
            cur.execute("ALTER TABLE correspondencias ADD COLUMN numero_rendicion TEXT")

        cur.execute("DROP TABLE IF EXISTS rendicion_detalle")
        cur.execute("DROP TABLE IF EXISTS rendiciones")

        cur.execute("""
            CREATE TABLE rendiciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                fecha TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'abierta',
                observacion TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE rendicion_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_rendicion INTEGER NOT NULL,
                id_correspondencia INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                resultado TEXT NOT NULL,
                fecha_rendicion TEXT NOT NULL,
                observacion TEXT,
                escaneado_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (id_rendicion) REFERENCES rendiciones(id),
                FOREIGN KEY (id_correspondencia) REFERENCES correspondencias(id),

                UNIQUE (id_rendicion, codigo)
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_rendicion_detalle_codigo
            ON rendicion_detalle(codigo)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_correspondencias_numero_rendicion
            ON correspondencias(numero_rendicion)
        """)

        conn.commit()

    print("Migración de rendición aplicada correctamente.")


if __name__ == "__main__":
    migrar()