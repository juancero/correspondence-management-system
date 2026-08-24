from database import get_connection


def generar_numero_despacho():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS proximo FROM despachos")
        row = cur.fetchone()
        return f"D{int(row['proximo']):06d}"


def crear_despacho():
    numero = generar_numero_despacho()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO despachos (numero, estado) VALUES (?, 'abierto')",
            (numero,)
        )
        conn.commit()

        return {
            "id": cur.lastrowid,
            "numero": numero
        }


def cerrar_despacho(id_despacho):
    with get_connection() as conn:
        conn.execute("""
            UPDATE despachos
            SET estado = 'cerrado'
            WHERE id = ?
        """, (id_despacho,))
        conn.commit()


def buscar_pieza(codigo):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, codigo, apellido_nombre, domicilio, localidad
            FROM correspondencias
            WHERE codigo = ?
        """, (codigo,))
        return cur.fetchone()


def agregar_pieza(id_despacho, pieza):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT estado
            FROM despachos
            WHERE id = ?
        """, (id_despacho,))
        despacho = cur.fetchone()

        if not despacho or despacho["estado"] != "abierto":
            return {
                "ok": False,
                "mensaje": "El despacho está cerrado o no existe"
            }

        cur.execute("""
            SELECT d.numero
            FROM despacho_detalle dd
            JOIN despachos d ON d.id = dd.id_despacho
            WHERE dd.id_correspondencia = ?
            LIMIT 1
        """, (pieza["id"],))

        ya_asignada = cur.fetchone()

        if ya_asignada:
            return {
                "ok": False,
                "mensaje": f"La pieza ya pertenece al despacho {ya_asignada['numero']}"
            }

        try:
            cur.execute("""
                INSERT INTO despacho_detalle (
                    id_despacho,
                    id_correspondencia,
                    codigo
                ) VALUES (?, ?, ?)
            """, (id_despacho, pieza["id"], pieza["codigo"]))

            cur.execute("""
                UPDATE correspondencias
                SET estado = 'despachada'
                WHERE id = ?
            """, (pieza["id"],))

            conn.commit()

            return {
                "ok": True,
                "mensaje": "OK"
            }

        except Exception:
            return {
                "ok": False,
                "mensaje": "Error al agregar pieza"
            }


def listar_piezas(id_despacho):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.codigo, c.apellido_nombre, c.domicilio, c.localidad
            FROM despacho_detalle d
            JOIN correspondencias c ON c.id = d.id_correspondencia
            WHERE d.id_despacho = ?
            ORDER BY d.id DESC
        """, (id_despacho,))
        return cur.fetchall()


def guardar_despacho_completo(piezas):
    despacho = crear_despacho()
    id_despacho = despacho["id"]

    with get_connection() as conn:
        cur = conn.cursor()

        for pieza in piezas:
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM despacho_detalle
                WHERE id_correspondencia = ?
            """, (pieza["id"],))

            ya_existe = cur.fetchone()["total"]

            if ya_existe:
                continue

            cur.execute("""
                INSERT INTO despacho_detalle (
                    id_despacho,
                    id_correspondencia,
                    codigo
                ) VALUES (?, ?, ?)
            """, (
                id_despacho,
                pieza["id"],
                pieza["codigo"]
            ))

            cur.execute("""
                UPDATE correspondencias
                SET estado = 'despachada'
                WHERE id = ?
            """, (pieza["id"],))

        conn.commit()

    return despacho


def pieza_ya_despachada(id_correspondencia):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT d.numero
            FROM despacho_detalle dd
            JOIN despachos d ON d.id = dd.id_despacho
            WHERE dd.id_correspondencia = ?
            LIMIT 1
        """, (id_correspondencia,))

        return cur.fetchone()


def quitar_pieza_de_despacho(id_despacho, codigo):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                c.id,
                c.codigo,
                c.estado,
                c.resultado_rendicion,
                c.numero_rendicion
            FROM despacho_detalle dd
            JOIN correspondencias c ON c.id = dd.id_correspondencia
            WHERE dd.id_despacho = ?
            AND c.codigo = ?
            LIMIT 1
        """, (id_despacho, codigo))

        pieza = cur.fetchone()

        if not pieza:
            return {
                "ok": False,
                "mensaje": "La pieza no pertenece a este despacho."
            }

        if pieza["estado"] == "rendida" or pieza["resultado_rendicion"] or pieza["numero_rendicion"]:
            return {
                "ok": False,
                "mensaje": "No se puede quitar una pieza ya rendida."
            }

        cur.execute("""
            DELETE FROM despacho_detalle
            WHERE id_despacho = ?
            AND id_correspondencia = ?
        """, (id_despacho, pieza["id"]))

        cur.execute("""
            UPDATE correspondencias
            SET estado = 'pendiente'
            WHERE id = ?
        """, (pieza["id"],))

        conn.commit()

        return {
            "ok": True,
            "mensaje": "Pieza quitada del despacho correctamente."
        }
