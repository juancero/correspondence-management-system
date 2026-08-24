from database import get_connection


def listar_motivos(activos_solo=True):
    with get_connection() as conn:
        cur = conn.cursor()

        sql = """
            SELECT id, nombre, codigo, activo
            FROM motivos_rendicion
        """

        if activos_solo:
            sql += " WHERE activo = 1"

        sql += " ORDER BY nombre ASC"

        cur.execute(sql)

        return cur.fetchall()


def crear_motivo(nombre, codigo):
    with get_connection() as conn:
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO motivos_rendicion (
                    nombre,
                    codigo,
                    activo
                )
                VALUES (?, ?, 1)
            """, (nombre, codigo))

            conn.commit()

            return {
                "ok": True,
                "mensaje": "Motivo creado correctamente"
            }

        except Exception:
            return {
                "ok": False,
                "mensaje": "Ya existe un motivo con ese código"
            }


def cambiar_estado_motivo(id_motivo, activo):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            UPDATE motivos_rendicion
            SET activo = ?
            WHERE id = ?
        """, (activo, id_motivo))

        conn.commit()
