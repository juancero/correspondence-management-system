from database import get_connection


def generar_numero_rendicion():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 AS proximo FROM rendiciones")
        row = cur.fetchone()
        return f"R{int(row['proximo']):06d}"


def crear_rendicion(fecha):
    numero = generar_numero_rendicion()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rendiciones (numero, fecha, estado)
            VALUES (?, ?, 'abierta')
        """, (numero, fecha))

        conn.commit()

        return {
            "id": cur.lastrowid,
            "numero": numero,
            "fecha": fecha
        }


def buscar_pieza(codigo):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                id,
                codigo,
                apellido_nombre,
                domicilio,
                localidad,
                estado,
                resultado_rendicion,
                fecha_rendicion,
                numero_rendicion
            FROM correspondencias
            WHERE codigo = ?
        """, (codigo,))
        return cur.fetchone()


def rendir_pieza(id_rendicion, numero_rendicion, fecha_rendicion, codigo, resultado):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, codigo, apellido_nombre, domicilio, localidad, estado, numero_rendicion
            FROM correspondencias
            WHERE codigo = ?
        """, (codigo,))

        pieza = cur.fetchone()

        if not pieza:
            return {
                "ok": False,
                "mensaje": f"No existe: {codigo}"
            }

        if pieza["estado"] == "rendida":
            return {
                "ok": False,
                "mensaje": f"La pieza ya fue rendida en {pieza['numero_rendicion'] or 'otra rendición'}"
            }

        try:
            cur.execute("""
                INSERT INTO rendicion_detalle (
                    id_rendicion,
                    id_correspondencia,
                    codigo,
                    resultado,
                    fecha_rendicion
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                id_rendicion,
                pieza["id"],
                pieza["codigo"],
                resultado,
                fecha_rendicion
            ))

            cur.execute("""
                UPDATE correspondencias
                SET 
                    estado = 'rendida',
                    resultado_rendicion = ?,
                    fecha_rendicion = ?,
                    numero_rendicion = ?
                WHERE id = ?
            """, (
                resultado,
                fecha_rendicion,
                numero_rendicion,
                pieza["id"]
            ))

            conn.commit()

            return {
                "ok": True,
                "mensaje": "OK",
                "pieza": pieza
            }

        except Exception:
            return {
                "ok": False,
                "mensaje": f"La pieza ya fue cargada en esta rendición: {codigo}"
            }


def listar_piezas_rendicion(id_rendicion):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.codigo,
                c.apellido_nombre,
                c.domicilio,
                c.localidad,
                rd.resultado,
                rd.fecha_rendicion
            FROM rendicion_detalle rd
            JOIN correspondencias c ON c.id = rd.id_correspondencia
            WHERE rd.id_rendicion = ?
            ORDER BY rd.id DESC
        """, (id_rendicion,))
        return cur.fetchall()


def guardar_rendicion_completa(fecha, piezas):
    rendicion = crear_rendicion(fecha)

    id_rendicion = rendicion["id"]
    numero_rendicion = rendicion["numero"]

    with get_connection() as conn:
        cur = conn.cursor()

        for pieza in piezas:

            cur.execute("""
                INSERT INTO rendicion_detalle (
                    id_rendicion,
                    id_correspondencia,
                    codigo,
                    resultado,
                    fecha_rendicion
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                id_rendicion,
                pieza["id"],
                pieza["codigo"],
                pieza["resultado"],
                fecha
            ))

            cur.execute("""
                UPDATE correspondencias
                SET
                    estado = 'rendida',
                    resultado_rendicion = ?,
                    fecha_rendicion = ?,
                    numero_rendicion = ?
                WHERE id = ?
            """, (
                pieza["resultado"],
                fecha,
                numero_rendicion,
                pieza["id"]
            ))

        conn.commit()

    return rendicion


def quitar_pieza_de_rendicion(id_rendicion, codigo):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                c.id,
                c.codigo,
                c.estado,
                c.numero_rendicion
            FROM rendicion_detalle rd
            JOIN correspondencias c ON c.id = rd.id_correspondencia
            WHERE rd.id_rendicion = ?
            AND c.codigo = ?
            LIMIT 1
        """, (id_rendicion, codigo))

        pieza = cur.fetchone()

        if not pieza:
            return {
                "ok": False,
                "mensaje": "La pieza no pertenece a esta rendición."
            }

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM despacho_detalle
            WHERE id_correspondencia = ?
        """, (pieza["id"],))

        tiene_despacho = cur.fetchone()["total"] > 0

        nuevo_estado = "despachada" if tiene_despacho else "pendiente"

        cur.execute("""
            DELETE FROM rendicion_detalle
            WHERE id_rendicion = ?
            AND id_correspondencia = ?
        """, (id_rendicion, pieza["id"]))

        cur.execute("""
            UPDATE correspondencias
            SET 
                estado = ?,
                resultado_rendicion = NULL,
                fecha_rendicion = NULL,
                numero_rendicion = NULL
            WHERE id = ?
        """, (nuevo_estado, pieza["id"]))

        conn.commit()

        return {
            "ok": True,
            "mensaje": f"Pieza quitada correctamente. Nuevo estado: {nuevo_estado}."
        }
